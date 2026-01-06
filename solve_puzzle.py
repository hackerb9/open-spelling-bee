#!/usr/bin/env python3

''' solve (cheat) puzzles '''

import params
import utils
import generate_puzzles

import os
import sys
from dataclasses import asdict

def solve(p):

    q = p['generation_info']['quality']
    if q['is_valid'] is False:
        print ('INVALID PUZZLE:', ', '.join(q['why_invalid']))

    print ('letters:', p['letters'])
    print ('total_score:', p['total_score'])
    print ('word_count:', p['word_count'])
    print ('pangram(s):', ', '.join(p['pangram_list']))
    print ()

    # print all answers
    for x in p['word_list']:
        score = x.get('score')

        # add 7 points if word is pangram
        if x['word'] in p['pangram_list']:
            score += + 7
        utils.print_table((x['word'],score), 2, 10)

    return

def scowl_search(letters:str):
    '''Search all Scowl files, even if ranked as obscure or invalid category'''
    center=letters[0]
    utils.scowl_lookup(f'^%*{center}%*$', letters)

def scowl_english_search(letters:str):
    '''Search all english-words Scowl files, even if ranked as obscure'''
    center=letters[0]
    utils.scowl_lookup(f'^%*{center}%*$', letters, 'word_lists/scowl-u8/english-words.*')

def main():
    
    # if -a given, then search SCOWL directly instead of using scowl.txt
    if len(sys.argv)>2 and '-a' in sys.argv:
        aflag=True
        sys.argv = [ x for x in sys.argv if x != '-a' ]

    # try to read an existing or new puzzle from command line
    try:
        puzzle_idx = sys.argv[1].strip().upper()
    except:
        puzzle_idx = None


    if not puzzle_idx:
        print ('Please enter a puzzle. Exiting...')
        exit(0)
        
    # choose standard sorting for all puzzle file names
    puzzle_idx = utils.sort_letters(puzzle_idx)

    if not aflag:
        # check validity of letters
        if not utils.check_letters(puzzle_idx):
            print('Exiting...', file=sys.stderr)
            exit(1)

        # load json puzzle data. Generate as needed, but do not save to disk.
        puzl = generate_puzzles.solve(puzzle_idx)
        if not puzl:
            print(f'Error: Could not solve "{puzzle_idx}"\n', file=sys.stderr)
            exit(1)
        # solve puzzle (cheat mode)
        solve(puzl)
    else:
        # Use alternate solving method for '-a' flag
        scowl_english_search(puzzle_idx)

if __name__ == "__main__":

    main()
 
