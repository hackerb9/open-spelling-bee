#!/usr/bin/env python3

''' play puzzles based on params.py PUZZLE_PATH_READ value'''

import params
import utils
from shutil import get_terminal_size
from textwrap import fill

import os
import sys
import random
from dataclasses import dataclass, asdict

@dataclass
class PlayerState:
    score = 0
    words = 0
    found = []
    pangram = False
    achievements =  { '50': False, '70': False, '85': False }
    hints = 0
    hints_used = 0

def play(puzzle):
    # "puzzle" is a Puzzle dataclass, see utils.py.

    print('Type !help or !h for help')
    print('Playing puzzle index:',puzzle.letters)
    print('Your letters are:',draw_letters_honeycomb(puzzle.letters))

    # pangram is worth 7 extra points
    puzzle.total_score = puzzle.total_score + 7 * puzzle.pangram_count
    
    print ('Max score:', puzzle.total_score)
    print ('Total words:', puzzle.word_count)
    print ('Uniqueness:', utils.uniqueness(puzzle.word_list))

    #print(puzzle.word_list) # no cheating!

    player = PlayerState()

    # loop until game ends
    while True:
        # ask user to guess a word
        guess = ask_user()

        # user need some help
        if guess in ('', '?'): guess="!h"
        if guess.startswith('!'):
            command(guess, puzzle, player)
            continue

        # already guessed that
        if guess in player.found:
            print ('You already found:',guess,'\n')
            continue
        
        # guess less than minimum letters
        if len(guess) < params.MIN_WORD_LENGTH:
            print (f'Guessed word is too short. Minimum length: {params.MIN_WORD_LENGTH}\n')
            continue           

        # scenario 1: includes letter not in a list
        if any([x for x in guess if x not in puzzle.letters]):
            print ('Invalid letter(s)','\n')
            continue

        # scenario 2: doesn't include center letter but all other letters valid
        if puzzle.letters[0] not in guess:
            print ('Must include center letter:',puzzle.letters[0],'\n')
            continue

        # find index of array for matching word, if any
        # https://stackoverflow.com/a/4391722/2327328
        word_index = next((index for (index, d) in enumerate(puzzle.word_list) if d['word'] == guess), None)

        if word_index is None:
            # scenario 4: not a valid word
            print ('Sorry,',guess,'is not a valid word','\n')
            continue
        elif guess in player.found:
            # scenario 5: good word but already found
            print ('You already found',guess,'\n')
            continue
        else:
            # word is valid and found
            word_dict = puzzle.word_list[word_index]

            player.words += 1

            word_score = word_dict.get('score')
            if word_dict.get('word') in puzzle.pangram_list:
                # pangrams are worth +7 extra
                word_score += 7
                player.pangram = True
                print ('\nPANGRAM!!!')
                #guess += '*'

            player.score += word_score

            print_list = [
                '✓ '+guess, \
                f'+{word_score} points', \
                f'{player.words}/{puzzle.word_count} words', \
                f'{player.score}/{puzzle.total_score} score', \
            ]

            if word_dict.get('word') in puzzle.pangram_list:
                print_list[0] += ' ***'

            # print success and running stats
            c = len(print_list)
            w = int(get_terminal_size().columns / c)
            utils.print_table(print_list, c, w)
            print()
            
            word_percent=round(player.words*100.0/puzzle.word_count,1)
            score_percent=round(player.score*100.0/puzzle.total_score,1)
            # Did they make it to 50% of words or score?
            if not player.achievements['50']:
                if word_percent >= 50 or score_percent >= 50:
                    player.achievements['50'] = True
                    print( fill('“GENIUS LEVEL ACHIEVED: You have found 50% of the hidden words! When you quit, any remaining words will be listed.”',
                                width=get_terminal_size().columns) )
                    print()

            # Did they make it to 70% of words or score?
            if not player.achievements['70']:
                if word_percent >= 70 or score_percent >= 70:
                    player.achievements['70'] = True
                    print( fill("“AMAZING: You've reached 70%! Next bonus at 85%.”" ) )
                    if player.hints>0:
                        offer_hint(player.hints_used, player.hints)
                    print()

            # Did they make it to 85% of words or score?
            if not player.achievements['85']:
                if word_percent >= 85 or score_percent >= 85:
                    player.achievements['85'] = True
                    print( fill('“SUPERBRAIN LEVEL ACHIEVED: You have found 85% of the hidden words!”', width=get_terminal_size().columns ) )
                    player.hints += 1
                    player.hints_used -= 1
                    print( fill('You get one free hint.' ) )
                    offer_hint(player.hints_used, player.hints)
                    print()

            # add good guess to the list, so it can't be reused
            player.found.append(guess)
        
        # all words found (somehow this could be possible)
        if player.words == puzzle.word_count:
            print ('Congratulations. You found them all!','\n')
            exit(0)

def shuffle_letters(game_letters):
    # shuffles letters, excluding the center letter
    # random.shuffle() only works in place
    other_letters = list(game_letters[1:])
    random.shuffle(other_letters)
    return game_letters[0] + ''.join(other_letters)

def draw_letters_honeycomb(game_letters):
    
    # taken from http://ascii.co.uk/art/hexagon

    if len(game_letters) != 7:
        # simple one-line printing for now
        # currently not used
        return game_letters[0]+' '+''.join(game_letters[1:])

    hex_string = r'''
            _____
           /     \
          /       \
    ,----(    {2}    )----.
   /      \       /      \
  /        \_____/        \
  \   {1}    /     \    {3}   /
   \      /       \      /
    )----(    {0}'   )----(
   /      \       /      \
  /        \_____/        \
  \   {4}    /     \    {5}   /
   \      /       \      /
    `----(    {6}    )----'
          \       /
           \_____/
'''

    return hex_string.format(*game_letters)

def ask_user():
    try:
        text = input('Your guess: ')
        text = text.strip().upper()
        return text
    except (EOFError, KeyboardInterrupt):
        print("Exiting...")
        exit(1)

def print_status(puzzle, player):
    width=get_terminal_size().columns
    if len(player.found) > 0:
        print (fill('found: ' + ', '.join(player.found[::-1]), width=width-8,
                    initial_indent=' '*4, subsequent_indent=' '*11))
    print (f'''\
    player words: {player.words} / {puzzle.word_count} ({round(player.words*100.0/puzzle.word_count,1)}%)
    player score: {player.score} / {puzzle.total_score} ({round(player.score*100.0/puzzle.total_score,1)}%)
    pangram found: {player.pangram}''')


def show_not_found(word_list, player_found):
    a=set( x['word'] for x in word_list )
    b=set(player_found)
    c=sorted( list(a-b) )
    if len(c) > 0:
        width=get_terminal_size().columns
        print( fill('not found: ' +', '.join(c), subsequent_indent=' '*11 , width=width))

def offer_hint(used, available):
    width=get_terminal_size().columns
    used_hints=f'{used} hint{"s" if used!=1 else ""}'
    print( fill(f'You have used {used_hints} and have {available} remaining. {"Use !hint to get a hint." if available>0 else ""}', width=width))

def command(msg, puzzle, player):
    
    # "!FOO" -> "foo"
    msg = msg[1:].lower()
    if msg == '': msg = 'i'     # ! by itself shows instructions
    if msg == 'help': msg = 'h'

    if msg == 'q' or msg == 'quit':
        print('Quitting...')
        print_status(puzzle, player)

        if player.achievements['50']:
            show_not_found(puzzle.word_list, player.found)
        exit(0)
    elif msg == 'h':
        print_help()
    elif msg == 'i':
        print_instructions()
    elif msg == 'g':
        print(draw_letters_honeycomb(puzzle.letters))
    elif msg == 'f':
        puzzle.letters = shuffle_letters(puzzle.letters)
        print(draw_letters_honeycomb(puzzle.letters))
    elif msg == 's':
        print_status(puzzle, player)
    else:
        print(f'Unknown command "!{msg}"')
        print_help()
    return

def print_help():
    print('!i : instructions\n!g : show letters\n!f : shuffle letters\n!s : player stats\n!h : this help\n!q : quit')

def print_instructions():
    print(f'''
    Welcome to the Open Source Spelling Bee puzzle!
    To play, build minimum {params.MIN_WORD_LENGTH}-letter words.
    Each word must include the center letter at least once.
    Letters may be used as many times as you'd like.

    Scoring: 1 point for a {params.MIN_WORD_LENGTH} letter word, and
             1 more point for each extra letter beyond that.
                Example:      WORD - 1 point
                             WORDS - 2 points
                          SPELLING - 5 points

    Each puzzle has {params.COUNT_PANGRAMS} pangram{"s" if params.COUNT_PANGRAMS!=1 else ""} that uses each of the {params.TOTAL_LETTER_COUNT} letters.
    The pangram is worth 7 extra points.

    To reach "genius" level, you'll need to solve 50% of the words.

    Have fun!
    ''')


def main():
    
    # try to read an existing or new puzzle from command line (not required)
    try:
        puzzle_idx = sys.argv[1].strip().upper()
    except:
        puzzle_idx = None

    if puzzle_idx is not None:
        
        # check validity of letters
        utils.check_letters(puzzle_idx)

        # choose standard sorting for all puzzle file names
        puzzle_idx = utils.sort_letters(puzzle_idx)

    puzl_path = utils.select_puzzle(puzzle_idx)
    puzl = utils.read_puzzle(puzl_path)
    play(puzl)

if __name__ == "__main__":

    main()
 
