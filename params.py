#!/usr/bin/env python3

''' parameter file for generate_puzzles.py '''

import os

# how many games to generate, and max number of attempts to try
PUZZLE_COUNT = 1000
MAX_PUZZLE_TRIES = 100000

# file paths
WORD_LIST_PATH = 'word_lists' + os.sep + 'scowl.txt'
PUZZLE_DATA_PATH = 'data'

# multithreading if more than 1
THREADS = 1

# set minimum word length and total letters used
MIN_WORD_LENGTH = 4
TOTAL_LETTER_COUNT = 7

VOWEL_LIST = ('A', 'E', 'I', 'O', 'U')

# set count of pangrams (suggested = 1)
COUNT_PANGRAMS = 1

# word count limits
MIN_WORD_COUNT = 25
MAX_WORD_COUNT = 50

# Reject games with too many simple pairs of words (LOVE, LOVES, LOVING, LOVED)
CAP_PLURALS = True		# -S (plural pairs)
MAX_PLURALS = 3
CAP_GERUNDS = True              # -ING (gerunds or present participles)
MAX_GERUNDS = 5
CAP_PRETERITE = True            # -ED (simple past tense)
MAX_PRETERITE = 7

# total score limits
MIN_TOTAL_SCORE = 60
#MAX_TOTAL_SCORE = 240
MAX_TOTAL_SCORE = 400           # Allow long words

WARN_INVALID_MANUAL = True      # Warn if a manually specified game is invalid 


# Should valid games be listed as they're found when running generate_puzzles?
# Values can be: "csv", "dots", or False.
PRINT_VALID = "csv"             # Emit table of puzzles, tab separated.
#PRINT_VALID = "dots"            # "dots" prints . for every valid game.

# Show rejected games as well as valid ones.
# "auto", "csv", "dots", "why", or None
PRINT_INVALID = "auto"           # None, if letters are picked randomly,
				 #   otherwise, use same as PRINT_VALID.
#PRINT_INVALID = "csv"           # Emit table of puzzles, tab separated.
#PRINT_INVALID = "dots"          # "dots" prints an "x" per invalid games.
#PRINT_INVALID = "why"           # "why" prints % stats for invalid games.

