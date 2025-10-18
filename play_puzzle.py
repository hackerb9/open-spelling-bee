#!/usr/bin/env python3

''' play puzzles based on params.py PUZZLE_PATH_READ value'''

import params
import utils
from shutil import get_terminal_size
from textwrap import fill

import os
import sys
import random

def play(puzl):
    print('Type !help or !h for help')

    letters = puzl.get('letters')
    print('Playing puzzle index:',letters)

#    letters = puzl.get('letters')
    print('Your letters are:',draw_letters_honeycomb(letters))

    word_list = puzl.get('word_list')
    pangram_list = puzl.get('pangram_list')
    # pangram is worth 7 extra points
    total_score = puzl.get('total_score') + 7 * int(puzl.get('pangram_count'))
    word_count = puzl.get('word_count')
    
    print ('Max score:',total_score)
    print ('Total words:', word_count)
    print ('Uniqueness:', utils.uniqueness(word_list))

    player_score = 0
    player_words = 0

    #print(word_list) # no cheating!

    guess_list = []
    player_pangram = False
    achievements = { '50': False, '70': False, '85': False }
    hints_available = 0
    hints_used = 0

    # loop until game ends
    while True:
        # ask user to guess a word
        guess = ask_user()

        # user need some help
        if guess in ('', '?'): guess="!h"
        if guess.startswith('!'):
            help(guess, letters, guess_list, player_score, player_words, player_pangram, total_score, word_count, word_list, achievements)
            continue

        # already guessed that
        if guess in guess_list:
            print ('You already found:',guess,'\n')
            continue
        
        # guess less than minimum letters
        if len(guess) < params.MIN_WORD_LENGTH:
            print (f'Guessed word is too short. Minimum length: {params.MIN_WORD_LENGTH}\n')
            continue           

        # scenario 1: includes letter not in a list
        if any([x for x in guess if x not in letters]):
            print ('Invalid letter(s)','\n')
            continue

        # scenario 2: doesn't include center letter but all other letters valid
        if letters[0] not in guess:
            print ('Must include center letter:',letters[0],'\n')
            continue

        # find index of array for matching word, if any
        # https://stackoverflow.com/a/4391722/2327328
        word_index = next((index for (index, d) in enumerate(word_list) if d['word'] == guess), None)

        if word_index is None:
            # scenario 4: not a valid word
            print ('Sorry,',guess,'is not a valid word','\n')
            continue
        elif guess in guess_list:
            # scenario 5: good word but already found
            print ('You already found',guess,'\n')
            continue
        else:
            # word is valid and found
            word_dict = word_list[word_index]

            player_words += 1

            word_score = word_dict.get('score')
            if word_dict.get('word') in pangram_list:
                # pangrams are worth +7 extra
                word_score += 7
                player_pangram = True
                print ('\nPANGRAM!!!')
                #guess += '*'

            player_score += word_score

            print_list = [
                '✓ '+guess, \
                f'+{word_score} points', \
                f'{player_words}/{word_count} words', \
                f'{player_score}/{total_score} score', \
            ]

            if word_dict.get('word') in pangram_list:
                print_list[0] += ' ***'

            # print success and running stats
            c = len(print_list)
            w = int(get_terminal_size().columns / c)
            utils.print_table(print_list, c, w)
            print()
            
            word_percent=round(player_words*100.0/word_count,1)
            score_percent=round(player_score*100.0/total_score,1)
            # Did they make it to 50% of words or score?
            if not achievements['50']:
                if word_percent >= 50 or score_percent >= 50:
                    achievements['50'] = True
                    print( fill('“GENIUS LEVEL ACHIEVED: You have found 50% of the hidden words! When you quit, any remaining words will be listed.”',
                                width=get_terminal_size().columns) )
                    print()

            # Did they make it to 70% of words or score?
            if not achievements['70']:
                if word_percent >= 70 or score_percent >= 70:
                    achievements['70'] = True
                    print( fill("“AMAZING: You've reached 70%! Next bonus at 85%.”" ) )
                    if hints_available>0:
                        offer_hint(hints_used, hints_available)
                    print()

            # Did they make it to 85% of words or score?
            if not achievements['85']:
                if word_percent >= 85 or score_percent >= 85:
                    achievements['85'] = True
                    print( fill('“SUPERBRAIN LEVEL ACHIEVED: You have found 85% of the hidden words!”', width=get_terminal_size().columns ) )
                    hints_available += 1
                    hints_used -= 1
                    print( fill('You get one free hint.' ) )
                    offer_hint(hints_used, hints_available)
                    print()


            # add good guess to the list, so it can't be reused
            guess_list.append(guess)
        
        # all words found (somehow this could be possible)
        if player_words == word_count:
            print ('Congratulations. You found them all!','\n')
            exit(0)

def shuffle_letters(letters):
    # shuffles letters, excluding the center letter
    # random.shuffle() only works in place
    other_letters = list(letters[1:])
    random.shuffle(other_letters)
    return letters[0] + ''.join(other_letters)

def draw_letters_honeycomb(letters):
    
    # taken from http://ascii.co.uk/art/hexagon

    if len(letters) != 7:
        # simple one-line printing for now
        # currently not used
        return letters[0]+' '+''.join(letters[1:])

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

    return hex_string.format(*letters)

def ask_user():
    try:
        text = input('Your guess: ')
        text = text.strip().upper()
        return text
    except (EOFError, KeyboardInterrupt):
        print("Exiting...")
        exit(1)

def show_status(guess_list, player_words, word_count, player_score, total_score, player_pangram, achievements):
    width=get_terminal_size().columns
    return fill('found: ' + ', '.join(guess_list[::-1]), width=width-8, initial_indent=' '*4, subsequent_indent=' '*11) + '\n' \
        f'    player words: {player_words} / {word_count} ({round(player_words*100.0/word_count,1)}%)\n' \
        f'    player score: {player_score} / {total_score} ({round(player_score*100.0/total_score,1)}%)\n' \
        f'    pangram found: {player_pangram}'


def show_not_found(word_list, guess_list):
    a=set( x['word'] for x in word_list )
    b=set(guess_list)
    c=sorted( list(a-b) )
    if len(c) > 0:
        width=get_terminal_size().columns
        print( fill('not found: ' +', '.join(c), subsequent_indent=' '*11 , width=width))

def offer_hint(used, available):
    width=get_terminal_size().columns
    used_hints=f'{used} hint{"s" if used!=1 else ""}'
    print( fill(f'You have used {used_hints} and have {available} remaining. {"Use !hint to get a hint." if available>0 else ""}', width=width))

def help(msg, letters, guess_list, player_score, player_words, player_pangram, total_score, word_count, word_list, achievements):
    
    # "!FOO" -> "foo"
    msg = msg[1:].lower()
    if msg == 'help': msg = 'h'
    if msg == '': msg = 'i'     # ! by itself shows instructions

    if msg == 'q' or msg == 'quit':
        print('Quitting...')
        print(show_status(guess_list, player_words, word_count, player_score, total_score, player_pangram, achievements))
        if achievements['50']:
            show_not_found(word_list, guess_list)
        exit(0)

    help_msg = '!i : instructions\n!g : show letters\n!f : shuffle letters\n!s : player stats\n!h : help\n!q : quit'
    instruction_msg = f'''
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
    '''

    msg_dict = {
        'h' : help_msg,
        'i' : instruction_msg,
        'g' : draw_letters_honeycomb(letters),
        'f' : draw_letters_honeycomb(shuffle_letters(letters)),
        's' : show_status(guess_list, player_words, word_count, player_score, total_score, player_pangram, achievements),
    }

    print(msg_dict.get(msg,f'Unknown command: {msg}'))
    return

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
 
