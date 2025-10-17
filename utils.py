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
        print ('You created a new puzzle:',puzl_idx)
        puzl_path = params.PUZZLE_DATA_PATH + os.sep + puzl_idx + '.json'
    
    return puzl_path

def read_puzzle(puzl_path):

    with open(puzl_path,'r') as fp:
        puzzles = json.load(fp)

    #print(len(puzzles.get('letters'),'total puzzle(s) were loaded')

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
                


if __name__ == "__main__":
        if len(sys.argv) <= 1:
                print( f'''\
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
                        print("Usage: cmp <filename1.json> <filename2.json>")
                        exit(1)

        elif (args[0] == "slook"):
                if len(args) > 2:
                        scowl_lookup(args[1])
                else:
                        print("Usage: slook <word>")
                        exit(1)

        else:
                print(f"Unknown command: {args[0]}")
                exit(1)
                
