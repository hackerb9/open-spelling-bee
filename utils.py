#!/usr/bin/env python3

''' helper functions that are used between different parts of the code '''

import params
import generate_puzzles

import os
import random
import json
import glob
import sys
import gzip
import re
from dataclasses import dataclass, asdict


# check validity of provided letters
def check_letters(pzl):

	if len(pzl) != len(list(set(pzl))):
		print('Invalid count of letters requested.', file=sys.stderr)
		print('Exiting...', file=sys.stderr)
		exit(1)

	elif len(pzl) != params.TOTAL_LETTER_COUNT:
		print('Invalid count of letters requested.', file=sys.stderr)
		print('Exiting...', file=sys.stderr)
		exit(1)
	else:
		return

# smart sorting of letters, keeping first letter first
def sort_letters(pzl):
	return pzl[0] + ''.join(sorted(pzl[1:]))


def select_puzzle(puzl_idx=None):

    puzzles = glob.glob(params.PUZZLE_DATA_PATH + os.sep + '*.json')
    puzl_idx_list = [x.split(os.sep)[-1].split('.')[0] for x in puzzles]

    # scenario 1: no selection made, so return a random puzzle
    if puzl_idx is None:
        # return a random puzzle
        puzl_path = random.choice(puzzles)
        print ('You selected a random puzzle:',puzl_path)
        return puzl_path

    if len(puzl_idx) != params.TOTAL_LETTER_COUNT:
        print ('Puzzles must be ',str(params.TOTAL_LETTER_COUNT),'letters long. Please try again.', file=sys.stderr)
        exit(1)

    # scenario 2: specific puzzle requested but not already available
    if puzl_idx in puzl_idx_list:
        print('Existing puzzle will be played:',puzl_idx)
        puzl_path = params.PUZZLE_DATA_PATH + os.sep + puzl_idx + '.json'
    # scenario 3: create a new puzzle because an existing one was not found
    else:
        puzl_idx = generate_puzzles.main(puzl_idx)
        puzl_path = params.PUZZLE_DATA_PATH + os.sep + puzl_idx + '.json'
        print ('You created a new puzzle:',puzl_path)
    
    return puzl_path

@dataclass
class Puzzle:
    letters: str
    generation_info: dict
    total_score: int
    word_count: int
    pangram_count: int
    pangram_list: list
    word_list: list

def read_puzzle(puzl_path):
    with open(puzl_path,'r') as fp:
        puzzles = Puzzle(**json.load(fp))
    return puzzles

def print_table(data, cols, wide):
    '''Prints formatted data on columns of given width.'''
    # https://stackoverflow.com/a/50215584/2327328
    n, r = divmod(len(data), cols)
    pat = '{{:{}}}'.format(wide)
    line = '\n'.join(pat * cols for _ in range(n))
    sys.stdout.reconfigure(encoding="utf-8")
    print(line.format(*data))
    #last_line = pat * r
    #print(last_line.format(*data[n*cols:]))

def uniqueness(word_list) -> float:
        '''
        Calculate a metric of how "unique" a puzzle's words are.

        Theoretical range is from 0.00 (monotonous) to 1.00 (unpredictable).
        English is naturally repetitive, so actual range is ~ 0.31 to 0.53.
        (0.31: GIKNOTW; 0.53: BACIORT)

        The purpose is to discard puzzles that are too repetitive.
        For example, 0.40: WIGGLE, WIGGLED, WRIGGLE, WRIGGLED, ...
        '''
        
        words = ''.join(x['word'] for x in word_list)
        original = len(words)
        compressed = len( gzip.compress( words.encode() ) )
        compressed = compressed - len( gzip.compress( ''.encode() ) )

        try:
                return round( compressed / original, 2 )
        except ZeroDivisonError:
                return 1.00

def get_puzzle_dir_or_filename(puzl_name=None):
        '''Given a DIRECTORY or FILENAME glob, return a list of filenames.

        A DIRECTORY (e.g., "data.twl/") returns all files that end in .json.
        A FILENAME ("data/YAEGLRU.json") returns that file.

        Globs are allowed ("data/YAEG*") to specify multiple files.
        Filename can omit "data/" prefix and ".json" suffix, ("YAEGLRU"),
        Letters can be lowercase ("yaeglru"). Globs are allowed ("yae*").
        If the shell is expanding the globs, quote it in single ticks:
        ./utils.py uniq '*y*'    shows all games with the letter 'Y'.

        Defaults to PUZZL_DATA_PATH ("data/").'''
        
        if puzl_name is None:
                return glob.glob(params.PUZZLE_DATA_PATH + os.sep + '*.json')

        if os.path.isdir(puzl_name):
                return glob.glob(puzl_name + os.sep + '*.json')

        puzzles = glob.glob(f"{params.PUZZLE_DATA_PATH}{os.sep}{puzl_name.upper()}.json")
        if len(puzzles) == 0:
                puzzles = glob.glob(puzl_name)
        if len(puzzles) == 0:
                print(f"No such directory or file '{puzl_name}'")
                exit(-1) 
        return puzzles


def check_uniqueness(*args):
        '''Read all data files and output a list of puzzles sorted by the uniqueness metric'''

        if len(args) == 0: args=[None]
        puzzles=[]
        for puzl_name in args:
                puzzles += get_puzzle_dir_or_filename(puzl_name)
        puzl_idx_list = [x.split(os.sep)[-1].split('.')[0] for x in puzzles]
        results = {}
        for puzl_path in puzzles:
                with open(puzl_path,'r') as fp:
                        puzl = json.load(fp)
                        word_list = puzl.get('word_list')
                        results[puzl_path] = uniqueness(word_list);
                        
        results = dict( sorted(results.items(), key=lambda i: i[1] ))
        for puzl_path in results:
                print( f"{results[puzl_path]}\t{puzl_path}" )
                

def compare_overlap(f1, f2):
        '''Given two puzzle names, show how much their words overlap.'''
        file1 = get_puzzle_dir_or_filename(f1).pop()
        file2 = get_puzzle_dir_or_filename(f2).pop()
        with open(file1,'r') as fp:
                puzl = json.load(fp)
                words1 = [x['word'] for x in puzl.get('word_list')]
                len1=len(words1)
        with open(file2,'r') as fp:
                puzl = json.load(fp)
                words2 = [x['word'] for x in puzl.get('word_list')]
                len2=len(words2)
        both=len(set(words1).intersection(words2))
        print(f"{file1:>30}: {len1:>2}")
        print(f"{file2:>30}: {len2:>2}")
        print(f"{'Words in both':>30}: {both:>2}")
        print(f"{'Overlap':>30}: {100*both/min(len1,len2):>5.2f}%")

def scowl_lookup_usage():
        print('''Usage: ./utils.py slook <pattern>

Shows words matching the given prefix (regular expression ^pattern.*)
and which wordlist file it was found in. The number at the end of the
filename is an indication of how common SCOWL thinks the word is. This
is useful to see why a word is getting rejected. The default threshold
is <=35, so english-words.35 is used but english-words.40 is not. 

    $ ./utils.py slook alfalfa
    word_lists/scowl/english-words.40: alfalfa
    word_lists/scowl/english-words.80: alfalfas

Too many matches? For the exact word, put a '$' at the end. For example,

    $ ./utils.py slook mes | wc -l
    914
    $ ./utils.py slook mes$
    word_lists/scowl/english-words.35: mes
''')


def scowl_lookup(pattern):
        '''Like the look(1) command, shows matches for "pattern" as a prefix,
        but searches through the SCOWL word_lists.
        Essentially: rgrep -i ^pattern word_lists/scowl

        NOTE: the SCOWL files we have are encoded as Latin-1, not UTF-8!

        If there are too many matches and you just want the exact
        word, just put a $ at the end. For example,

            $ ./utils.py slook mes | wc -l
            914
            $ ./utils.py slook mes$ | wc -l
            2
        '''

        if type(pattern) is not list:
                pattern = [ pattern ]

        for p in pattern:
                regex=re.compile(fr'^{p}.*', flags=re.IGNORECASE|re.MULTILINE)
                for f in sorted(glob.glob("word_lists/scowl/*"), key=scowl_sort):
                        with open(f, 'r', encoding='ISO-8859-1') as fp:
                                output=re.findall(regex, fp.read())
                                for w in output:
                                        try:
                                                print(f'{f}: {w}')
                                        except BrokenPipeError:
                                                sys.stdout = None

def scowl_sort(fullpath):
        '''Given a filename of the form "english-words.35", return a tuple with extension first so that it will be the primary sort key.'''
        name, ext = os.path.splitext(fullpath)
        try:
                ext = int(ext[1:])
        except ValueError:
                ext = 999

        return (ext, name)


                
if __name__ == "__main__":
        if len(sys.argv) <= 1:
                print(f'''\
Usage: {sys.argv[0]} <cmd> [opts]

where <cmd> can be one of:

  uniq [dir...]
                print a "uniqueness" score for all .json files in "data/"
                (Entropy from approx 0.4 to 0.6)

  cmp <f1> <f2>
                compare two files from data/*.json and show how many
                words they have in common.
		
  slook <word>
                lookup prefix <word> in all the SCOWL wordlists (common & rare)
''')
                exit(1)
        
        args=sys.argv[1:]
        
        if (args[0] == "uniq"):
                if len(args) > 1:
                        check_uniqueness(*args[1:])
                else:
                        check_uniqueness()

        elif (args[0] == "cmp"):
                if len(args) > 2:
                        compare_overlap(args[1], args[2])
                else:
                        print('''\
Usage: {sys.argv[0]} cmp <puzzle1> <puzzle2>
Examples:
          ./utils.py cmp rceimnu rceimnp
          ./utils.py cmp yaeglru  data/YAEGLRT.json
          ./utils.py cmp data.twl/CADEHKW.json  data/CADEHKW.json''');
                        exit(1)

        elif (args[0] == "slook"):
                if len(args) > 1:
                        scowl_lookup(args[1])
                else:
                        scowl_lookup_usage()
                        exit(1)

        else:
                print(f"Unknown command: {args[0]}")
                exit(1)
                
