#!/usr/bin/env python3

''' generate puzzles based on criteria in params.py '''

import params
import utils

import os
import sys
import string
import random
from multiprocessing import Pool as ThreadPool
import itertools
import json
import glob

def get_existing_puzzles():

    # return list of previously generated puzzles
    
    existing_puzzles = glob.glob(params.PUZZLE_DATA_PATH + os.sep + '*.json')
    existing_puzzles = [x.replace(params.PUZZLE_DATA_PATH + os.sep,'').replace('.json','') for x in existing_puzzles]
    return existing_puzzles

def get_words(word_file):

    # https://github.com/jmlewis/valett/
    # https://raw.githubusercontent.com/jmlewis/valett/master/scrabble/sowpods.txt

    # http://scrabutility.com/TWL06.txt

    with open(params.WORD_LIST_PATH,'r') as wp:
        words = wp.readlines()

    # trim whitespace and remove short words
    words = [w.strip().upper() for w in words if len(w.strip()) >= params.MIN_WORD_LENGTH]

    # remove words known to be too obscure (e.g., "geed", "geeing")
    try:
        remove_list=utils.get_custom_word_list('remove')
        words = sorted(list( set(words) - set(remove_list) ))
    except (OSError, IOError) as e:
        print(f'Could not read optional "remove" list: {e}')

    # add words which are known to be missing (e.g., "groundhog", "druid")
    try:
        add_list=utils.get_custom_word_list('add')
        if words and add_list:
            words = sorted(list( set(words).union(set(add_list)) ))
    except (OSError, IOError) as e:
        print(f'Could not read optional "add" list: {e}')

    return words

def get_letters():

    alphabet_list = list(string.ascii_uppercase)

    while True:
        # generate sample of alphabet (can inlcude each letter only once)
        random_list = random.sample(alphabet_list, params.TOTAL_LETTER_COUNT)

        # make sure each letter list includes at least one vowel
        if [i for i in random_list if i in params.VOWEL_LIST]:
            return utils.sort_letters(''.join(random_list))

def get_letters_from(letters_list):
    # pick one entry at random, then shuffle the letters
    letters = random.choice(letters_list)
    letters = ''.join(random.sample(letters,len(letters)))
    return utils.sort_letters(letters)

def get_pangramable_letter_pool(all_words):
    # reduce list of words to 7+ letter words that have exactly 7 unique letters
    big_words = [w.strip() for w in all_words if len("".join(set(w)).strip()) == params.TOTAL_LETTER_COUNT]

    # strip duplicate letters and sort
    big_words = list(map(lambda word: ''.join(sorted(''.join(set(word)))), big_words))

    # remove duplicate "words"
    big_words = list(set(big_words))

    return big_words

def check_words(letters, word):

    letters = list(letters)

    # filter logic: must include any letter from list, as well as the first item
    if all(x in set(letters) for x in word) and letters[0] in word:

        # calculate the score of the word
        score = get_score(word)

        # check if word is pangram of letters
        if all(x in set(word) for x in letters):
            #print ('pangram:', word, letters)
            return {'word' : word , 'score' : score, 'pangram' : True}
        else:
            return {'word' : word , 'score' : score, 'pangram' : False}
    else:
        # no matching words found
        return None

def get_score(word):

    # simple scoring algorithm. Maybe use MIN_WORD_LENGTH?
    if len(word) == 4:
        return 1
    else:
        return len(word)


# For debugging, number of valid games found during this run.
valid_count = 0


# For PRINT_INVALID='why', accumulator for reasons games are being rejected.
why_cumulative={ 'Already found': 0, 'Too few pangrams': 0, 'Too many pangrams': 0,
         'Total score too low': 0, 'Total score too high': 0,
         'Too few words': 0, 'Too many words': 0,
         'Too many plural pairs': 0, 'Too many gerund pairs': 0,
         'Too many preterite pairs': 0}

def print_cumulative_why(why):
    '''Given an associative array indicating why a set of letters was
    invalid, add those results to the running total in why_cumulative 
    and print out the results.

    If multiple reasons are indicated, then fractional amounts are
    added for each reason in why_cumulative.

    This is useful to tune to the params.py file to a specific
    dictionary if too few games are being generated.
    '''
    global why_cumulative

    print()
    print("Reasons why generated games were rejected:")
    for k in why:
        why_cumulative[k] += why[k]/len(why)
    total = sum(why_cumulative[k] for k in why_cumulative)
    for k in why_cumulative:
        print( '%24s: %5.2f%%' % (k, 100*why_cumulative[k]/total) )
    print()
    print('%24s: %d' % ( 'Valid games found', valid_count ), flush=True )


def make_puzzles(word_list, pool, existing_puzzles, letters=None):
    is_valid=True       # Are the current letters a valid game? 
    why_invalid={}      # Reasons why current letters are invalid.
    global valid_count  # Count of valid games found.
    manual_puzzle=False # Were the letters specified? (False is automatic)
    s_pairs = ed_pairs = ing_pairs = 0        # For pruning less fun puzzles.

    if letters is not None:
        manual_puzzle = True    # Caller specified what letters to use
    else:
        letters = get_letters_from(pool) # E.G. 'WAHORTY'
        if letters in existing_puzzles:
            return False

    results = []
    if params.THREADS > 1:
        pool = ThreadPool(params.THREADS)
        results = pool.starmap(check_words, zip(itertools.repeat(letters), word_list))
    else:
        for word in word_list:
            results.append(check_words(letters, word))

    # remove None from list
    results = list(filter(None, results))

    # get total score of all words
    total_score = sum([x.get('score') for x in results])

    # generate list of pangrams
    pangram_list = list(filter(lambda x: x.get('pangram'), results))

    # Count up potentially problematic pairs. LOVE, LOVES, LOVED, LOVING, 
    if 'S' in letters: s_pairs = count_plurals(results)
    if all([x in letters for x in 'ED']): ed_pairs = count_preterite(results)
    if all((x in letters for x in 'ING')): ing_pairs = count_gerunds(results)

    # check if generated answers are invalid, based on params
    # incorrect number of pangrams
    # OR total_score falls out of bounds
    # OR total number of words falls out of bounds
    # OR too many pairs of singular/plural (FOOL, FOOLS) 
    # OR too many pairs of verb/gerund/pp (ENHANCE, ENHANCING)
    # OR too many pairs of verb/preterit (YODEL, YODELED)
    if (len(pangram_list) < params.COUNT_PANGRAMS):
        is_valid=False
        why_invalid['Too few pangrams']=1
    if (len(pangram_list) > params.COUNT_PANGRAMS):
        is_valid=False
        why_invalid['Too many pangrams']=1
    if (total_score < params.MIN_TOTAL_SCORE):
        is_valid=False
        why_invalid['Total score too low']=1
    if (total_score > params.MAX_TOTAL_SCORE):
        is_valid=False
        why_invalid['Total score too high']=1
    if (len(results) < params.MIN_WORD_COUNT):
        is_valid=False
        why_invalid['Too few words']=1
    if (len(results) > params.MAX_WORD_COUNT):
        is_valid=False
        why_invalid['Too many words']=1
    if (params.CAP_PLURALS and s_pairs > params.MAX_PLURALS):
        is_valid=False
        why_invalid['Too many plural pairs']=1
    if (params.CAP_GERUNDS and ing_pairs > params.MAX_GERUNDS):
        is_valid=False
        why_invalid['Too many gerund pairs']=1
    if (params.CAP_PRETERITE and ed_pairs > params.MAX_PRETERITE):
        is_valid=False
        why_invalid['Too many preterite pairs']=1

    if not is_valid:
        # not valid! 
        # (manual puzzles create files whether valid or not)
        if not manual_puzzle:
            if params.PRINT_INVALID == "dots":
                print ('.', end='', flush=True)
            elif params.PRINT_INVALID == "why":
                print_cumulative_why(why_invalid)
            elif params.PRINT_INVALID == "csv":
                print( letters, len(results), total_score, len(pangram_list),
                       is_valid, s_pairs, ed_pairs, ing_pairs, sep='\t' )
            # return to go to next letters.
            return False
        else:
            # Not valid, but puzzle was specified manually
            if params.PRINT_INVALID == "dots":
                print ('', flush=True, file=sys.stderr)
            print(f'Warning: Game written to {letters}.json'
                  ' despite the following errors:\n\t',
                  ', '.join(why_invalid), '.', flush=True, file=sys.stderr)

    # We got a valid word list (or manually specified), so let folks know.
    if params.PRINT_INVALID == "dots" != params.PRINT_VALID:
        print ('')          # Newline after row of .....

    if params.PRINT_VALID == "dots":
        print ('!', end='', flush=True)
    elif params.PRINT_VALID == "csv":
        print( letters, len(results), total_score, len(pangram_list),
               is_valid, s_pairs, ed_pairs, ing_pairs, sep='\t' )

    # If you made it this far, the game will be recorded.
    # WARNING! if puzzle already exists, it will be overwritten
    file_path = params.PUZZLE_DATA_PATH + os.sep + letters + '.json'

    valid_count += int(is_valid)

    if manual_puzzle and letters in existing_puzzles:
        # We were given specific letters despite the puzzle already
        # existing. This is likely to quickly regenerate the file
        # using new params, therefore we'll set "manual_puzzle" to
        # whatever its previous value was in the existing file.
        puzl = utils.read_puzzle(file_path)
        manual_puzzle = puzl.generation_info['manual_puzzle']

    pangram_list = [x.get('word') for x in pangram_list ]

    generation_info = {
        'path'               : params.WORD_LIST_PATH,
        'min_word_length'    : params.MIN_WORD_LENGTH,
        'total_letter_count' : params.TOTAL_LETTER_COUNT,
        'min_word_count'     : params.MIN_WORD_COUNT,
        'max_word_count'     : params.MAX_WORD_COUNT,
        'min_total_score'    : params.MIN_TOTAL_SCORE,
        'max_total_score'    : params.MAX_TOTAL_SCORE,
        'cap_plurals'        : params.CAP_PLURALS,
        'max_plurals'        : params.MAX_PLURALS,
        'cap_gerunds'        : params.CAP_GERUNDS,
        'max_gerunds'        : params.MAX_GERUNDS,
        'count_pangrams'     : params.COUNT_PANGRAMS,
        'manual_puzzle'      : manual_puzzle,
    }

    tmp = {
            'letters' : letters, # key letter is always first in list
            'generation_info' : generation_info,
            'total_score' : total_score,
            'word_count' : len(results),
            'pangram_count' : len(pangram_list),
            'pangram_list' : pangram_list,
            'word_list' : results,
        }

    with open(file_path, 'w') as json_file:
        json.dump(tmp, json_file, indent=4)

    return is_valid

def count_plurals(results):
    """Given a list of words, return the number of pairs which appear as
    both singular and plural form in the list (adding -S or -ES).

    For example: CHEESE, CHEESES, CLICHE, CLICHES, HEEL, HEELS
    would return 3.

    This allows one to reject games which have too high of a count
    of plural pairs. (See params.py:MAX_PLURALS). The reasoning is
    that it would be boring to have to repeatedly type the same
    word twice, such as:

    ['APPLAUSE', 'GAUGE', 'GAUGES', 'GLUE', 'GLUES', 'GUESS', 'GUESSES', 'GULL', 'GULLS', 'GULP', 'GULPS', 'LEAGUE', 'LEAGUES', 'LUGGAGE', 'LUGS', 'LULL', 'LULLS', 'PAUSE', 'PAUSES', 'PLAGUE', 'PLAGUES', 'PLUG', 'PLUGS', 'PLUS', 'PLUSES', 'PULL', 'PULLS', 'PULP', 'PULPS', 'PULSE', 'PULSES', 'PUPS', 'PUSS', 'PUSSES', 'SAUSAGE', 'SAUSAGES', 'SLUG', 'SLUGS', 'SUES', 'SUPPLE', 'USAGE', 'USAGES', 'USELESS', 'USES', 'USUAL']

    """

    words = list(x['word'] for x in results)
    count=0
    for word in words:
        if not word.endswith('S'):
            continue
        if word[0:-1] in words:
            count=count+1
        if not word.endswith('ES'):
            continue
        if word[0:-2] in words:
            count=count+1
    return count


def count_gerunds(results):
    """Given a list of words, return the number of pairs which appear as
    both verb and gerundive noun form in the list (adding -ING,
    possibly doubling previous letter, possibly removing -E
    suffix).

    For example: LOVE, LOVING, YODEL, YODELING, ZIGZAG, ZIGZAGGING
    would return 3.

    Limiting the count (see params.py:MAX_GERUNDS) allows games
    with 'I', 'N', and 'G' to exist, but rejects games that are
    too simple because too many words end in -ING.
    """

    words = list(x['word'] for x in results)
    count=0
    for word in words:
        if not word.endswith('ING'):
            continue
        if word[0:-3] in words:
            count=count+1       # YODELING -> YODEL
        if word[0:-3]+'E' in words:
            count=count+1       # LOVING -> LOVE
        if len(word) >= 5 and word[-4] == word[-5] and word[0:-4] in words:
            count=count+1       # YODELLING -> YODEL (British English)
    return count


def count_preterite(results):
    """Given a list of words, return the number of pairs which appear as
    both the verb and the simple past tense by adding -ED or -D. 

    For example: LOVE, LOVED, YODEL, YODELED, ZIGZAG, ZIGZAGGED
    would return 3.

    Limiting the count (see params.py:MAX_PRETERITE) allows games
    with 'E', 'D', to exist, but rejects games that are too simple
    because too many words end in -ED. """

    words = list( x['word']  for x in results )
    count=0
    for word in words:
        if not word.endswith('ED'):
            continue
        if word[0:-2] in words:
            count=count+1       # YODELED -> YODEL
        if word[0:-1] in words:     
            count=count+1       # LOVED -> LOVE
        if len(word) >= 4 and word[-3] == word[-4] and word[0:-3] in words:
            count=count+1       # YODELLED (British English)
    return count
def main(puzzle_input=None):

    try:
        # if data dir does not exist, create it
        if not os.path.isdir(params.PUZZLE_DATA_PATH):
            os.makedirs(params.PUZZLE_DATA_PATH)

        # get array of previously generated puzzles, to check against
        existing_puzzles = get_existing_puzzles()

        words = get_words(params.WORD_LIST_PATH)
        #words = words[0:10000] #debug
        print ('total words: ', len(words))
        pool = get_pangramable_letter_pool(words)
        print (f'unique {params.TOTAL_LETTER_COUNT}-letter pool: '+str(len(pool)))

        if len(sys.argv) > 1 and sys.argv[-1] == '--regenerate':
            regenerate = True
            sys.argv.pop()
        else:
            regenerate = False

        if len(sys.argv) > 1:
            puzzle_input = sys.argv[-1].strip().upper()
            sys.argv.pop()
        else:
            puzzle_input = None

        # header for csv output
        if params.PRINT_INVALID == "csv":
            print ('\t'.join(('letters', 'words', 'score', 'pangram', 'valid?', '-S pair', '-ED', '-ING')))

        # user has requested a specific puzzle be created
        if puzzle_input is not None:
            # check validity of letters
            utils.check_letters(puzzle_input)

            # manually request one puzzle by defining letters  on command line
            # alphabetize the non-center letters (all but first in array)
            puzzle_input = utils.sort_letters(puzzle_input)

            make_puzzles(words, pool, existing_puzzles, puzzle_input)

        elif regenerate:
            # Regenerate all existing puzzles
            no_good=[]
            try:
                for puzzle_input in existing_puzzles:
                    if not make_puzzles(words, [], existing_puzzles, puzzle_input):
                        no_good.append(puzzle_input)
            except KeyboardInterrupt:
                print("Aborting.")
            if no_good:
                print(f'These puzzles no longer meet the requirements and can be deleted:\n{" ".join(no_good)}')

        # user/code has no specific puzzle to create, generating many
        else:

            idx_valid = 0

            # generating N puzzles based on params
            for _ in range(params.MAX_PUZZLE_TRIES):
                if make_puzzles(words, pool, existing_puzzles, None):
                    idx_valid += 1

                # reached target count of puzzles, exiting loop
                if idx_valid >= params.PUZZLE_COUNT:
                    exit(0)

        return puzzle_input
    except KeyboardInterrupt:
        print("Exiting.")
        return -1
        
if __name__ == "__main__":
    main()
