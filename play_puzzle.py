#!/usr/bin/env python3

''' play puzzles based on params.py PUZZLE_PATH_READ value'''

import params
import utils
from shutil import get_terminal_size
from textwrap import fill

import os
import sys
import random
import re
from dataclasses import dataclass, asdict

@dataclass
class PlayerState:
    score = 0
    words = 0
    found = []
    pangram = False
    achievements =  { '50': False, '70': False, '85': False }
    bonus_found = []
    bonus_used = []
    hints_available = 0
    hints_used = 0
    hint_penalty = 1
    hints_given = {}
    last_hint = ""
    lastguess = 'anomia'


def splitwords(s, x='!"#$%&''()*+,-./0123456789:;<=>?@[\\]^_` '):
    '''Split string to array of alphabetic by non-alpha without using regexp'''
    y=' '*len(x)
    t=str.maketrans(x,y)
    return s.translate(t).split()


def play(puzzle):
    # "puzzle" is a Puzzle dataclass, see utils.py.

    print('Type !i for instructions or !h for command help')
    print('Playing puzzle index:',puzzle.letters)
    print('Your letters are:',draw_letters_honeycomb(puzzle.letters))

    # pangram is worth 7 extra points
    puzzle.total_score = puzzle.total_score + 7 * puzzle.pangram_count

    utils.print_table([f'Max score: {puzzle.total_score}', 
                       f'Total words: {puzzle.word_count}',
                       f'Uniqueness: {utils.uniqueness(puzzle.word_list)}'])

    #print(puzzle.word_list) # no cheating!

    player = PlayerState()

    # loop until game ends
    while True:
        # ask user to guess a word
        guess = ask_user()

        # user need some help
        if guess in ('', '!redraw'): guess="!g"
        if guess in ('?', '!?'): guess="!h"
        if guess.startswith('!'):
            command(guess, puzzle, player)
            continue

        player.lastguess = guess 		# Save for later ! commands

        for g in re.findall(r'\w+', guess):
                g=g.upper()

                # Is word easily dismissable?
                if g in player.found:
                    print ('You already found:',g,'\n')
                    continue
                if len(g) < puzzle.generation_info.get("min_word_length", 0):
                    print (f'Guessed word is too short. Minimum length: {puzzle.generation_info.get("min_word_length", 0)}\n')
                    continue
                if any([x for x in g if x not in puzzle.letters]):
                    print ('Invalid letter(s)','\n')
                    continue
                if puzzle.letters[0] not in g:
                    print ('Must include center letter:',puzzle.letters[0],'\n')
                    continue

                # find index of array for matching word, if any
                # https://stackoverflow.com/a/4391722/2327328
                word_index = next((index for (index, d) in enumerate(puzzle.word_list) if d['word'] == g), None)

                if word_index is None:
                    if utils.is_bonus_word(g):
                        if g in player.bonus_found or g in player.bonus_used:
                            print (f'You already found: {g}\n')
                        else:
                            print (f'Oh! I was not expecting anyone to guess "{g}". Kudos to you!\n')
                            player.bonus_found.append(g)
                    else:
                        print (f'Sorry, "{g}" is not a valid word\n')
                    continue

                else:
                    # word is valid and found
                    player.words += 1

                    # add good guess to the list, so it can't be reused
                    player.found.append(g)

                    word_dict = puzzle.word_list[word_index]
                    word_score = word_dict.get('score')
                    if word_dict.get('word') in puzzle.pangram_list:
                        # pangrams are worth +7 extra
                        word_score += 7
                        player.pangram = True
                        print ('\nPANGRAM!!!')
                        #g += '*'

                    player.score += word_score

                    print_list = [
                        '✓ '+g, \
                        f'+{word_score} points', \
                        f'{player.words}/{puzzle.word_count} words', \
                        f'{player.score}/{puzzle.total_score} score', \
                    ]

                    if word_dict.get('word') in puzzle.pangram_list:
                        print_list[0] += ' ***'

                    if word_dict.get('word') in player.hints_given:
                        player.last_hint=""

                    # print success and running stats
                    utils.print_table(print_list)
                    print()

                    word_percent=round(player.words*100.0/puzzle.word_count,1)
                    score_percent=round(player.score*100.0/puzzle.total_score,1)
                    # Did they make it to 50% of words or score?
                    if not player.achievements['50']:
                        if word_percent >= 50 or score_percent >= 50:
                            player.achievements['50'] = True
                            print( fill('“AMAZING: You have found 50% of the hidden words! When you quit, any remaining words will be listed.”',
                                        initial_indent=' '*3,
                                        subsequent_indent=' '*4,
                                        width=get_terminal_size().columns-8) )
                            print()

                    # Did they make it to 70% of words or score?
                    if not player.achievements['70']:
                        if word_percent >= 70 or score_percent >= 70:
                            player.achievements['70'] = True
                            print( fill("“GENIUS LEVEL ACHIEVED: You've reached 70%!”",
                                        initial_indent=' '*3,
                                        subsequent_indent=' '*4,
                                        width=get_terminal_size().columns-8) )
                            if player.hints_available>0:
                                offer_hint(player.hints_used, player.hints_available)
                            print()

                    # Did they make it to 85% of words or score?
                    if not player.achievements['85']:
                        if word_percent >= 85 or score_percent >= 85:
                            player.achievements['85'] = True
                            print( fill('“SUPERBRAIN LEVEL ACHIEVED: You have found 85% of the hidden words!”',
                                        initial_indent=' '*3,
                                        subsequent_indent=' '*4,
                                        width=get_terminal_size().columns-8) )
                            player.hints_available += 1
                            offer_hint(player.hints_used, player.hints_available)
                            print()

        # all words found (somehow this could be possible)
        if player.words == puzzle.word_count:
            print ('Congratulations. You found them all!','\n')
            print_status(puzzle, player)
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

def ask_user(prompt='Your guess: '):
    try:
        text = input(prompt)
        text = text.strip()
        return text
    except (KeyboardInterrupt):
        print("Exiting...")
        exit(1)
    except (EOFError):
        return ""

def ranking(score, maxscore):
    p = 100 * score / maxscore
    if p == 100:
        return "Queen Bee"
    elif p >= 85:
        return "Super-Brain"    # Not official NYT, but useful for usa
    elif p >= 70:
        return "Genius"
    elif p >= 50:
        return "Amazing"
    elif p >= 40:
        return "Great"
    elif p >= 25:
        return "Nice"
    elif p >= 15:
        return "Solid"
    elif p >= 8:
        return "Good"
    elif p >= 5:
        return "Moving Up"
    elif p >= 2:
        return "Good Start"
    elif p >= 0:
        return "Beginner"
    else:
        return "Uh-oh"

def print_status(puzzle, player):
    utils.print_table([
        f'score: {player.score:>3} / {puzzle.total_score:>3} ({round(player.score*100.0/puzzle.total_score,1):>5.1f}%)',
        f'{ranking(player.score, puzzle.total_score).upper():>3}',
        f'words: {player.words:>3} / {puzzle.word_count:>3} ({round(player.words*100.0/puzzle.word_count,1):>5.1f}%)',
        f'pangram found: {player.pangram}',
        f'hints used: {player.hints_used}',
        f'hints available: {player.hints_available}'])
    if player.last_hint:
        print(f'last hint: {player.last_hint}')
    if player.found:
        width=get_terminal_size().columns
        print (fill('found: ' + ', '.join(player.found[::-1]), width=width-8,
                    initial_indent=' '*4, subsequent_indent=' '*11))
    if player.bonus_found:
        width=get_terminal_size().columns
        print (fill('bonus: ' + ', '.join(player.bonus_found[::-1]), width=width-8,
                    initial_indent=' '*4, subsequent_indent=' '*11))
    print()

def get_not_found(word_list, player_found):
    a=set( x['word'] for x in word_list )
    b=set(player_found)
    c=sorted( list(a-b) )
    return c

def show_not_found(word_list, player_found):
    c = get_not_found(word_list, player_found)
    if len(c) > 0:
        width=get_terminal_size().columns
        print( fill('not found: ' + ', '.join(c), subsequent_indent=' '*11 , width=width))

def offer_hint(used, available):
    free_hints=f'{available} free hint{"s" if available!=1 else ""}'
    print( fill(f'You have {free_hints}. {"Use !hint." if available else ""}',
                initial_indent=' '*4, subsequent_indent=' '*4,
                width=get_terminal_size().columns-8))

def give_hint(puzzle, player):
    '''Show a hint by revealing a letter of the longest unfound word.'''
    word = get_longest_unfound(puzzle.word_list, player.found)
    if player.hints_given.get(word, 0) == len(word):
        print(player.last_hint)
        print()
        return
    if (player.hints_available > 0):
        player.hints_available -= 1
    else:
        if player.bonus_found:
            reply = ask_user(f"It'll cost you a bonus word. Are you sure? ")
            if len(reply)==0 or reply[0].upper() != 'Y':
                print()
                return
            else:
                player.bonus_used.append( player.bonus_found.pop() )
                print(f'forfeited "{player.bonus_used[-1]}"')
                player.hints_used += 1
        else:
            cost = 2**player.hint_penalty - 1
            reply = ask_user(f"It'll cost you {cost} point{s(cost)}. Are you sure? ")
            if len(reply)==0 or reply[0].upper() != 'Y':
                print()
                return
            player.score -= cost
            player.hint_penalty += 1
            player.hints_used += 1
    if not word in player.hints_given:
        player.hints_given[word] = 0
    if player.hints_given[word] < len(word):
        player.hints_given[word] += 1
    x=player.hints_given[word]
    y=len(word) - player.hints_given[word]
    player.last_hint = word[0:x] + '_'*y + f' ({str(len(word))} letters)'
    print( player.last_hint )
    print()

def get_longest_unfound(word_list, player_found):
    c = get_not_found(word_list, player_found)
    c = sorted(c, key=len)
    return c[-1]

def s(n:int) -> str:
    '''An "s" for plural numbers, e.g., "3 points"'''
    return "" if n == 1 else "s"
    
def command(command, puzzle, player):
    '''Player gave a !cmd command, so do the action requested'''
    command = command.split()
    cmd = command[0].lower()[1:]    # "!FOO" -> "foo"
    cmdargs = command[1:]

    if cmd == '': cmd = 'h'     # ! by itself shows the game commands

    if cmd == 'q' or cmd == 'quit':
        print('Quitting...')
        print_status(puzzle, player)
        if player.achievements['50']:
            show_not_found(puzzle.word_list, player.found)
        exit(0)
    elif cmd == 'h':
        print_short_commands()
    elif cmd == 'help':
        print_full_commands()
    elif cmd == 'i':
        print_instructions()
    elif cmd == 'g':
        print(draw_letters_honeycomb(puzzle.letters))
    elif cmd == 'f':
        puzzle.letters = shuffle_letters(puzzle.letters)
        print(draw_letters_honeycomb(puzzle.letters))
    elif cmd == 's':
        print_status(puzzle, player)
    elif cmd == 'hint':
        give_hint(puzzle, player)
    elif cmd == 'dict' or cmd == 'define' or cmd == 'wb':
        if cmdargs: player.lastguess=cmdargs
        utils.dict_define( player.lastguess )
    elif cmd == 'match' or cmd == 'm':
        if cmdargs: player.lastguess=cmdargs
        utils.match_any( player.lastguess )
    elif cmd == 'scowl' or cmd == 'slook':
        if cmdargs: player.lastguess=cmdargs
        utils.scowl_lookup( player.lastguess )
    else:
        print(f'Unknown command "!{cmd}"')
        print_short_commands()
    return

def print_short_commands():
    utils.print_table([ '!s : player stats', '!g : show letters', '!f : shuffle letters', '!i : instructions', '!q : quit', '!help: all commands' ])
    print()

def print_full_commands():
    utils.print_table([ '!s : player stats and found words', '!g : show honeycomb of letters', '!i : game instructions',  '!f : shuffle letters', '!h : short command list', '!q : quit' ])
    print()
    print('''\
Extended commands
    !hint             : Request a hint.
    !dict   [word]    : Define word in dictionary (if available).
    !match  [word]    : Check for headword (regex) in SCOWL and dict.
    !ok     [word...] : Accept this word in the future as a bonus word.
    !add    [word...] : Add to the wordlist used to generate new puzzles.
    !remove [word...] : Remove from wordlist when generating puzzles.

    Note: "[word...]" means zero, one, or more words are allowed.
          If no words are specified, the last guess will be used.
    ''')
    print('''\
Special keys
    ENTER on an empty line shows the letters, same as !g.
    Ctrl-U erases current guess. Ctrl-C exits immediately.
    ''')


def print_instructions():
    print(f'''
    Welcome to the Open Source Spelling Bee puzzle!
    To play, spell {params.MIN_WORD_LENGTH}-letter or longer words.
    Each word must include the center letter at least once.
    Letters may be used as many times as you'd like, in any order.

    Scoring: 1 point for a {params.MIN_WORD_LENGTH}-letter word, and +1 for each extra letter.
                Example:      WORD : 1 point
                             WORDY : 2 points
                            WORKED : 3 points
                          WOODWORK : 5 points

    Each puzzle has {params.COUNT_PANGRAMS} pangram{"s" if params.COUNT_PANGRAMS!=1 else ""} that uses each of the {params.TOTAL_LETTER_COUNT} letters.
    The pangram is worth 7 extra points.
                       *** KEYWORD : 4 points + 7 points

    To reach "AMAZING" level, you'll need to solve 50% of the words.
    Type "!h" to see game commands.

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
