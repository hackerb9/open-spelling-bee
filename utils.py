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
import subprocess
from dataclasses import dataclass, asdict
from shutil import get_terminal_size

class ScowlFile:
        '''A representation of a single subcorpus from the SCOWL wordlists.
        For example, the file "english-words.35"'''
        def __init__(self, filename=""):
                self.filename = filename
                self.category, ext = os.path.splitext(os.path.basename(filename))
                try:
                        ext = int(ext[1:])
                except ValueError:
                        ext = 999
                self.rank = ext
        def __repr__(self):
                return f'{self.rank}\t{self.category}\t({self.filename})'
        def __lt__(self, other):
                if (self.rank != other.rank):
                        return self.rank < other.rank
                else:
                        return self.category < other.category


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

def print_table(data, cols=None, wide=None):
        '''Prints formatted data on columns of given width.
           data is an array, cols is number of columns, wide is column width.
           If no width given, then terminal width / cols is used.
           If cols isn't given, then the fewest rows will be used.
        '''
        if not cols:
                m = max([len(s) for s in data]) + 2
                cols = int(get_terminal_size().columns / m)
                if cols > len(data):
                        cols = len(data)
        if not wide:
                wide = int(get_terminal_size().columns / cols)
        n, r = divmod(len(data), cols)
        pat = f'{{:{wide}}}'
        line = pat * cols
        sys.stdout.reconfigure(encoding="utf-8")
        for i in range(0, n*cols, cols):
                print(line.format(*data[i:i+cols]).rstrip())
        if r:
                line = pat * r
                print(line.format(*data[n*cols:]).rstrip())

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
        try:
                for puzl_path in results:
                        print( f"{results[puzl_path]}\t{puzl_path}" )
        except BrokenPipeError:
                pass

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


def custom_lookup(pattern):
        '''Grep the custom word lists for pattern and prints results.

        Custom words are kept in word_lists/dict-{add,okay,remove,*}.txt. 
        If 'pattern' is an array, then each word will be looked up.
        Allows regular expressions.
        '''

        if type(pattern) is not list:
                pattern = [ pattern ]

        for p in pattern:
                rx=re.compile(fr'^({p})$', flags=re.IGNORECASE|re.MULTILINE)
                for f in glob.glob("word_lists/dict-*.txt"):
                        with open(f, 'r') as fp:
                                output=re.findall(rx, custom_parse(fp.read()))
                                for w in output:
                                        try:
                                                print(f'{f}: {w}')
                                        except BrokenPipeError:
                                                sys.stdout = None

def is_in_custom(pattern):
        '''Returns the filenames of the custom word lists which match
        the regex 'pattern'.

        Custom words are kept in word_lists/dict-{add,okay,remove,*}.txt. 
        If 'pattern' is an array, then each word will be looked up.
        Allows regular expressions.

        If pattern is not in any of the files, an empty list is returned.
        '''

        rv = []

        if type(pattern) is not list:
                pattern = [ pattern ]

        for p in pattern:
                rx=re.compile(fr'^({p})$', flags=re.IGNORECASE|re.MULTILINE)
                for f in glob.glob("word_lists/dict-*.txt"):
                        with open(f, 'r') as fp:
                                output=re.findall(rx, custom_parse(fp.read()))
                                for w in output:
                                        rv+=(f'{f}')

custom_parse_re = re.compile(r'\W*(#.*)?\n|\W+')
def custom_parse(s: str) -> str:
        '''Given an entire custom word list file as a string,
        return just newline separated words, omitting comments,
        whitespace, and punctuation (except apostrophe).
        Input example:	"foo, bar (quux) madam's # this is a comment"
        '''
        return re.sub(custom_parse_re, '\n', s)

def is_bonus_word(w:str) -> [str]:
        '''If w is found in the bonus dictionaries, return an
        array of strings indicating which dictionaries it was found in.
        If it is not found, an empty list is returned.

        The bonus dictionaries are: 
	        word_lists/dict-{add,okay,remove}.txt,
		scowl-u8/english-words.{40,50)
        	dict lookup [not yet implemented]
        '''
        w=w.casefold()
        results=[]
        bonus_dicts=[]
        bonus_dicts += ('word_lists/dict-add.txt','word_lists/dict-okay.txt','word_lists/dict-remove.txt')
        bonus_dicts += [ x for x in glob.glob("word_lists/scowl-u8/english-words.*")
                         if 35 < scowl_rank(x) <= 50 ]
        for f in bonus_dicts:
                with open(f, 'r') as fp:
                        customwords=custom_parse(fp.read()).casefold().split()
                        if w in customwords:
                                results.append(f)
        return results

def is_in_scowl(w:str) -> []:
        '''If w is found in the scowl dictionaries, return an array of
        ScowlFile items indicating which wordlists matched and at what
        rank. Unlike is_bonus_word(), this searches other categories
        beyond english-words, such as british-english and variants.

        Returns an empty list if no match was found.

        '''
        w=w.casefold()
        results=[]
        for f in glob.glob("word_lists/scowl-u8/*"):
                with open(f, 'r') as fp:
                        words=fp.read().casefold().split()
                        if w in words:
                                results.append(ScowlFile(f))
        return sorted(results)

def scowl_lookup_usage():
        print(

        '''Usage: ./utils.py scowl <pattern>

Shows words matching the exact word (regular expression ^pattern$) and
which wordlist file it was found in. The number at the end of the
filename is an indication of how common SCOWL thinks the word is. This
is useful to see why a word is getting rejected. The default threshold
for generating puzzles is <=35, so english-words.35 is used but
english-words.40 is not.

To see possible inflections of a word, append .* like so:

    $ ./utils.py scowl alfalfa.*
    word_lists/scowl-u8/english-words.40: alfalfa
    word_lists/scowl-u8/english-words.40: alfalfa's
    word_lists/scowl-u8/english-words.80: alfalfas

''')


def scowl_lookup(pattern):
        '''Grep the SCOWL word_lists for ^(pattern)$ and print results'''

        if type(pattern) is not list:
                pattern = [ pattern ]

        for p in pattern:
                rx=re.compile(fr'^({p})$', flags=re.IGNORECASE|re.MULTILINE)
                for f in sorted(glob.glob("word_lists/scowl-u8/*"), key=scowl_sort):
                        with open(f, 'r') as fp:
                                output=re.findall(rx, fp.read())
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


def scowl_lookup_usage():
        print('''Usage: ./utils.py scowl <pattern>

Shows words matching the exact word (regular expression ^pattern$) and
which wordlist file it was found in. The number at the end of the
filename is an indication of how common SCOWL thinks the word is. This
is useful to see why a word is getting rejected. The default threshold
for generating puzzles is <=35, so english-words.35 is used but
english-words.40 is not.

To see possible inflections of a word, append .* like so:

    $ ./utils.py scowl alfalfa.*
    word_lists/scowl-u8/english-words.40: alfalfa
    word_lists/scowl-u8/english-words.80: alfalfas

''')


def scowl_lookup(pattern):
        '''Grep the SCOWL word_lists for ^pattern$
        If a list is given, then each word will be looked up.
        Allows regular expressions.

        NOTA BENE: we have re-encoded our SCOWL files to UTF-8, so we
        don't have to do deal with the Latin-1 encoding here.
        '''

        if type(pattern) is not list:
                pattern = [ pattern ]

        for p in pattern:
                rx=re.compile(fr'^({p})$', flags=re.IGNORECASE|re.MULTILINE)
                for f in sorted(glob.glob("word_lists/scowl-u8/*"), key=scowl_sort):
                        with open(f, 'r') as fp:
                                output=re.findall(rx, fp.read())
                                for w in output:
                                        try:
                                                print(f'{f}: {w}')
                                        except BrokenPipeError:
                                                sys.stdout = None

def scowl_category(fullpath: str) -> str:
        '''Given a filename ("wordlists/scowl-u8/english-words.35"),
        return the basename without the extension. ("english-words").'''

        name, ext = os.path.splitext(os.path.basename(fullpath))
        return name

def scowl_rank(fullpath: str) -> int:
        '''Given a filename of the form "english-words.35",
        return the integer which is the filename's extension.
        If the extension is not an integer, then return 999.'''
        name, ext = os.path.splitext(fullpath)
        try:
                ext = int(ext[1:])
        except ValueError:
                ext = 999
        return ext

def scowl_sort(fullpath: str) -> ():
        '''Given a filename of the form "english-words.35", return a tuple with extension first so that it will be the primary sort key.'''
        name, ext = os.path.splitext(fullpath)
        try:
                ext = int(ext[1:])
        except ValueError:
                ext = 999
        return (ext, name)


def dict_define_usage():
        print('''\
Usage: ./utils.py dict <word>
Looks up definitions for <word> in the dictionary.
(Runs `dict` as a subprocess.)
''')

def dict_define(pattern) -> int:
        '''Look up the definition of pattern in the dictionary.
        Note: uses the external 'dict' command.
        '''

        dictcmd='dict'
        (rc, dummy) = subprocess.getstatusoutput(f'type {dictcmd}')
        if rc == 127:
                print(f'Error: Is the "{dictcmd}" command installed?')
                return rc

        pipepager = get_pager()
        if pipepager:
                pipepager = '|' + pipepager

        if type(pattern) is list:
                pattern = ' '.join(pattern)

        cmdline = f'dict "{pattern}" {pipepager}' 
        rc = subprocess.run(cmdline, shell=True)
        return rc.returncode

def get_pager() -> str:
        '''Look up the PAGER environment variable and return it.
        Defaults to "less" + options.'''

        if 'PAGER' in os.environ and os.environ["PAGER"]:
                pager=os.environ["PAGER"]
        else:
                pager="less"

        pagerargs=""
        if pager == "less":
                pagerargs+='--prompt="M(Press space for more; q to quit; / to search.)" '
                pagerargs+='--no-init ' # Do not clear screen
                pagerargs+='-R '        # Show raw ANSI color sequences
                pagerargs+='-i '        # Search case insensitively
                pagerargs+='-F '        # No pager if def'n fits on screen.
                pagerargs+='-e '        # Exit on space at the end.

        (rc, dummy) = subprocess.getstatusoutput(f'type {pager}')
        if rc == 0:
                return f'{pager} {pagerargs}'
        else:
                return ''

def dict_lookup(pattern, showerrors=True):
        '''Show matching headwords in the dictionary.
        Allows regular expressions.
        Note: uses the external 'dict' command.
        '''
        if type(pattern) is list:
                pattern = ' '.join(pattern)

        dictcmd='dict'
        (rc, output) = subprocess.getstatusoutput(f'type {dictcmd}')
        if rc == 127:
                if showerrors:
                        print(f'Error: Is the "{dictcmd}" command installed?')
                return rc

        if type(pattern) is list:
                pattern = ' '.join(pattern)

        # We always anchor to the head and tail using ^{pattern}$.
        # That would cause pattern='kona|koan' to fail, so we add parens: ^({pattern})$.
        # But that triggers a bug in dict, so we add more parens: (^({pattern})$)
        cmdline = f'dict -m -s re "(^({pattern})$)"'   # Exact, but allow regex
        (rc, output) = subprocess.getstatusoutput(cmdline)
        if rc == 0:
                print(output)
                return 0
        else:
                cmdline = f'dict -m "{pattern}"'     # Allow correction
                (rc, output) = subprocess.getstatusoutput(cmdline)
                if rc == 0:
                        print(f'Headword "{pattern}" not found in dictionary, '
                              'perhaps you mean:')
                        print(output)
                elif showerrors:
                        print(f'Headword "{pattern}" not found in dictionary.')
                return rc


def match_any(pattern):
        '''Given a word (or regex), show which wordlists contain it using
        the custom dictionaries, SCOWL wordlists, and the 'dict' command.
        No error is printed if dict is not available on the system.'''
        custom_lookup(pattern)
        scowl_lookup(pattern)
        dict_lookup(pattern, showerrors=False)


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
		
  dict <word>   define word using the 'dict' command, if installed

  scowl <re>    lookup regex ^re$ in all the SCOWL wordlists. The
                numeric suffix shows how common the word is in English.

  match <re>    lookup regex ^re$ using dict, shows headword only

  lookup <re>   shows output from both scowl and match

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

        elif (args[0] == "scowl" or args[0] == "slook"):
                if len(args) > 1:
                        scowl_lookup(args[1:])
                else:
                        scowl_lookup_usage()
                        exit(1)

        elif (args[0] == "dict" or args[0] == "wb"):
                if len(args) > 1:
                        dict_define(args[1:])
                else:
                        dict_define_usage()
                        exit(1)

        elif (args[0] == "dict-m"):
                if len(args) > 1:
                        dict_lookup(args[1:])
                else:
                        print("Usage: ./utils.py dict-m <word>")
                        print("Shows matching headwords using dict")
                        exit(1)

        elif (args[0] == "match" or args[0] == "m"):
                if len(args) > 1:
                        match_any(args[1:])
                else:
                        print("Usage: ./utils.py match <word>")
                        print("Shows matching headwords using both SCOWL and dict")
                        exit(1)

        else:
                print(f"Unknown command: {args[0]}")
                exit(1)
                
