# Open Spelling Bee (OSB)

# 🐝

Open source port of New York Times' puzzle game [Spelling Bee][NYT] for the command line.

[NYT]: https://www.nytimes.com/puzzles/spelling-bee "The New York Times Spelling Bee"


Requires Python 3.x and nothing but standard Python libraries.

![Screenshot of OSB in a terminal window][screenshot]

[screenshot]: README.md.d/screenshot.webp "How many words can you spell from DEKORYW?"


## to play

To download the game:

    git clone https://github.com/philshem/open-spelling-bee.git
    cd open-spelling-bee

To play a random game:

    python3 play_puzzle.py

To play a non-random game:

    python3 play_puzzle.py RDGHNOU

where `R` is the center letter that must be used at least once in each word. If the puzzle `RDGHNOU` does not exist, it will be created and saved to `data/RDGHNOU.json` (the file names are the first letter and the alphabetically sorted remaining letters).

The word list used is from [SCOWL](http://wordlist.aspell.net/). The default setting contains 40,000 words, which seems comparable to the New York Times dictionary. (See below on changing the size parameter to include more erudite words.)

To reach "AMAZING" level, you'll need to solve 50% of the words.

To solve a game (aka cheat-mode):

    python3 solve_puzzles.py RDGHNOU

If the game does not exist, it will be created and saved to the `data/` folder. 

For a list of the previous NY Times letter selections, see [William Shunn's sbsolver][sbsolver].

[sbsolver]: https://www.sbsolver.com/s/1 "WAHORTY: May 9, 2018"

## to generate new puzzles

Set custom parameters in the `params.py` file, for example how many puzzles you want to create. Then generate by running:

    python3 generate_puzzles.py

Or to save the word stats:

    python3 generate_puzzles.py > stats.csv

Runtime depends on your parameters. For the default parameter settings, the code takes approximately 8 hours to generate 100 7-letter puzzles that meet the criteria (total points, total words, pangram count).

To generate a certain letter combination, use:

    python3 generate_puzzles.py AGFEDCB

which will then be saved to `data/ABCDEFG.json`.

## to change the size of the wordlist

If you find the game overly facile or wish your recondite words were accepted, you can change the wordlist size. Change `size=35` to a larger number in [word_lists/mkscowl](word_lists/mkscowl) and then run `mkscowl` to create a new wordlist. You must run `generate_puzzles.py` (as detailed above) whenever the wordlist changes.

|Description|Scowl size|Num words|Sample word|
|-|-|-|-|
|Small|`size=35`|40,198|abacus|
|Medium|`size=50`|63,375|abeyance|
|Large|`size=70`|115,332|abecedarian|
|Huge|`size=80`|251,064|abapical|
|Insane|`size=95`|435,726|abigailship|

---

# Game Play

To play, build words with a minimum of 4 letters, using the letters provided.

Each word must include the center letter at least once.

Letters may be used as many times as you'd like and in any order.

Scoring: 1 point for a 4 letter word, and 1 more point for each additional letter.

                Example:      WORD : 1 point
                             WORDY : 2 points
                            WORKED : 3 points
                          WOODWORK : 5 points

Each puzzle has 1 "pangram" that uses each of the 7 letters at least once. The pangram is worth 7 extra points.

                       *** KEYWORD : 4 points + 7 points


## example play

(based on game found by playing `python3 play_puzzle.py RDGHNOU`)

```
Type !i for instructions or !h for command help
Playing puzzle index: RDGHNOU
Your letters are: 
            _____
           /     \
          /       \
    ,----(    N    )----.
   /      \       /      \
  /        \_____/        \
  \   H    /     \    U   /
   \      /       \      /
    )----(    R'   )----(
   /      \       /      \
  /        \_____/        \
  \   G    /     \    D   /
   \      /       \      /
    `----(    O    )----'
          \       /
           \_____/

Max score: 88
Total words: 37

Your guess: HOUNDDOG
Must include center letter: R 

Your guess: GROG
✓ GROG                word score = 1        words found = 1/37    total score = 1/88    

Your guess: GODHOOD
✓ GODHOOD             word score = 4        words found = 2/37    total score = 5/88    
```

Use the following commands for more details:
```

Your guess: !h
!s : player stats     !g : show letters     !f : shuffle letters
!i : instructions     !q : quit             !help: all commands
```

---

## interesting puzzles

+ High "uniqueness" score (answers are dissimilar): `EAINTXY`, `BACIORT`, `IACMORT`

+ `Q` as center letter: `QAHILSU`, `QBEISTU`

+ `X` as center letter: `XACESTV`, `XEFIOST`, `XAENSTU`, `XADEIRS`, `XAEINOT`, `XCENOST`, `XEFIPRS`, `XAERSTY`, `XDELOPS`, `XBELOST`, `XCDELSU`

+ `Z` as center letter: `ZORIBTE`, `ZRBEOSU`, `ZCEILST`,`ZAEMNST`,`ZADELRS`, `ZADENRS`, `ZAEIKLS`, `ZACENOS`, `ZGILNOS`, `ZABDELR`, `ZBEGINO`, `ZABGINS`, `ZEILNOR`, `ZABDELS`, `ZAELOST`

+ Play tester faves: `RCEIMNU`, `ECHOPRY`, `NACEGHL`, `ECIQRTU`, `VAEGIRT`, `IACLPRT`

+ Especially challenging: `RCEIMNP`, `TACHIMR`, `VAEGIRT`

+ Historic: 
  * [ ] on or before 2004 November 1 (The Times of London, [Polygon][Polygon])
  * [ ] 2014 (Will Shortz proposes Spelling Bee based on Polygon)
  * 2015 February 22 `PADEQUR` (Frank Longo publishes first print Spelling Bee in NYT Magazine)
  * 2018 May 9: `WAHORTY` May 9, 2018 (Sam Von Ehren releases first digital NYT Spelling Bee online)
  * 2025 March 12: `FLOSUAB` (Sam Ezersky creates first NYT Spelling Bee to include the letter `S`)

[Polygon]: https://www.thetimes.com/article/how-to-play-polygon-gw30jlb39h2

--

## Scoring Levels

| Rank       | Score |
|------------|------:|
| BEGINNER   |    0% |
| GOOD START |    2% |
| MOVING UP  |    5% |
| GOOD       |    8% |
| SOLID      |   15% |
| NICE       |   25% |
| GREAT      |   40% |
| AMAZING    |   50% |
| GENIUS     |   70% |
| SUPERBRAIN |   85% |
| QUEEN BEE  |  100% |

Note, the original NYT ranking does not include 85%, but we added it
because it is a common place for players to bog down.


| Percent words or score | Effect                                                  |
|-----------------------:|---------------------------------------------------------|
|                     0% |                                                         |
|                     2% |                                                         |
|                     5% |                                                         |
|                     8% |                                                         |
|                    15% |                                                         |
|                    25% |                                                         |
|                    40% |                                                         |
|                    50% | List of unfound words will be shown upon quitting       |
|                    70% | (Earned hints become available? -- not implemented yet) |
|                    85% | One free hint                                           |
|                   100% | Game Over: You Win!                                     |


## To do

See [the todo list](todo.md) for random thoughts of what may come.

Suggestions are welcome! Just file an
[issue](https://github.com/hackerb9/open-spelling-bee/issues) on
github.
