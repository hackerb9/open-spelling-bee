#!/usr/bin/env python3

''' solve (cheat) puzzles '''

import params
import utils

import os
import sys
from dataclasses import asdict

def solve(p):

    print ('letters:', p.letters)
    print ('total_score:', p.total_score)
    print ('word_count:', p.word_count)
    print ('pangram(s):', ', '.join(p.pangram_list))
    print ()

    # print all answers
    for x in p.word_list:
        score = x.get('score')

        # add 7 points if word is pangram
        if x['word'] in p.pangram_list:
            score += + 7
        utils.print_table((x['word'],score), 2, 10)

    return

def main():
    
    # try to read an existing or new puzzle from command line (not required)
    try:
        puzzle_idx = sys.argv[1].strip().upper()
    except:
        print ('Please enter a puzzle. Exiting...')
        exit(0)

    if puzzle_idx is not None:
        
        # choose standard sorting for all puzzle file names
        puzzle_idx = utils.sort_letters(puzzle_idx)

        # check validity of letters
        if not utils.check_letters(puzzle_idx):
            print('Exiting...', file=sys.stderr)
	    exit(1)

    # select puzzle, generate it if it doesn't exist
    puzl_path = utils.select_puzzle(puzzle_idx)

    # load json puzzle data
    puzl = utils.read_puzzle(puzl_path)

    # solve puzzle (cheat mode)
    solve(puzl)

if __name__ == "__main__":

    main()
 
