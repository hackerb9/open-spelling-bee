# Open Spelling Bee (OSB)

# 🐝

Open source port of New York Times' puzzle game Spelling Bee for the command line.

Requires Python 3.x and nothing but standard Python libraries.

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

To reach "genius" level, you'll need to solve 50% of the words.

To solve a game (aka cheat-mode):

    python3 solve_puzzles.py RDGHNOU

If the game does not exist, it will be created and saved to the `data/` folder. 

For a list of the previous NY Times letter selections, see [William Shunn's page](https://www.shunn.net/bee/?past=1).

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

Letters may be used as many times as you'd like.

Scoring: 1 point for a 4 letter word, and 1 more point for each additional letter.

Each puzzle has 1 "pangram" that uses each of the 7 letters at least once. The pangram is worth 7 extra points.



## example play

(based on game found by playing `python3 play_puzzle.py RDGHNOU`)

```
Type !help or !h for help
Playing puzzle index: 1
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
Your guess: GROUND
✓ GROUND              word score = 3        words found = 1/37    total score = 3/88    
```

Use the following commands for more details:
```
!i : instructions
!g : show letters
!f : shuffle letters
!s : player stats
!h : help
!q : quit
```

---

## interesting puzzles

+ High "uniqueness" score: `EAINTXY`, `BACIORT`, `IACMORT`

+ `Q` as center letter: `QAHILSU`, `QBEISTU`

+ `X` as center letter: `XACESTV`, `XEFIOST`, `XAENSTU`, `XADEIRS`, `XAEINOT`, `XCENOST`, `XEFIPRS`, `XAERSTY`, `XDELOPS`, `XBELOST`, `XCDELSU`

+ `Z` as center letter: `ZORIBTE`, `ZRBEOSU`, `ZCEILST`,`ZAEMNST`,`ZADELRS`, `ZADENRS`, `ZAEIKLS`, `ZACENOS`, `ZGILNOS`, `ZABDELR`, `ZBEGINO`, `ZABGINS`, `ZEILNOR`, `ZABDELS`, `ZAELOST`

+ Play tester faves: `RCEIMNU`, `ECHOPRY`, `NACEGHL`, `ECIQRTU`, `VAEGIRT`, `IACLPRT`

+ Especially challenging: `RCEIMNP`, `TACHIMR`, `VAEGIRT`

## To do

### Deal with too many rejected words

Too many words are being refused. Example: IACLNOV:

    avian, iconic, laconic, clinician, cilia, loci, aioli, cavil,
    convivial, cannoli, oilcan, voila, parry, aurora, pyro, purl,
	parlay, orally, aurally

* [ ] `!A` should add words to a user dictionary for later analysis.

* [ ] Use that dict to figure out what SCOWL dictionary is best.

* [ ] Give player extra points for words which are not in the
  generating dictionary but are valid in more recondite sources.
  (Check user dict, more scowl, or maybe online dictd).

* [ ] Super points for a second PANGRAM; volcanic / convivial.


### Remove unininteresting puzzles 

Too many words with the same suffix or prefix. For example: `WAGINOV`
in which more than half of the words end in -ING.

* [x] Use compression to detect repetitiveness of words. "Uniqueness
      score" is ratio of compressed to original size.

  * [x] Can we reject if uniqueness is below a certain percentage? No.

  * It is true that the uninteresting puzzles have low uniqueness
    scores, usually below 50% (WAGINOV uniqueness = 0.47)...

  * However, some puzzles with low "uniqueness" are interesting (e.g.,
    `RCEIMNP`, uniq = 0.42). 
	
* [x] Are there puzzles which have a repetitive suffix and yet are
      still interesting? Yes. Maybe.

  * `TAIMNOV`, uniq = 0.42, contains many similar words, but finding
    them was challenging and not redundant as they all had unique
    meanings. (initiation, innovation, intonation, invitation,
    intimation, imitation, annotation, aviation, animation, ...).

  * There are even -ING heavy puzzles that are fun (e.g., `ICGNOTV`, uniq = 0.38).

* [ ] Perhaps what gets players annoyed is when they have to inflect
      every word: WAGE, WAGED, WAGGLE, WAGGLED, BADGE, BADGED

  * [ ] Can we check for that? Is there an easy way to stem a word so
        we can count the actual number of root words?

### Place found words to the side of the grid

* [ ] While probably distracting if it was always shown, it may be
  nice to sometimes have the words the user has found printed to the
  side of the puzzle. The list probably should be printed in columns
  so as to maximize the distance from the puzzle.

### Commands to add words to user lists

The user should be able to quickly add words to a list when they
come up during play.

There should be at least three word lists.

1. [ ] **ADD**: Add this word to the dictionary used to generate puzzles in
   the future. (E.g., AURORA, LINGUINI, FALAFEL, ALFALFA, UNICYCLING
   are not in the current default dictionary.)
   
2. [ ] **REMOVE**: This word should be on the "stoplist" so it will not be
   used to generate puzzles.

   This is necessary because the SCOWL dictionary this program
   currently uses has many words in the "top 35% of English" list
   which simply are not common enough to be there. For example:

   | Common homonym | Rare verb conjugations |
   |----------------|------------------------|
   | GEE            | GEED, GEEING           |
   | DIN            | DINNED, DINNING        |
   | HARE           | HARED, HARING          |
   | ALIEN          | ALIENED, ALIENING      |

   While those rare conjugations are perfectly valid English, they do
   not make for very fun puzzles. Many of the words appear to be an
   automated attempt to conjugate "common verbs", but the root word is
   not actually a verb in its common usage.

   There are also some words which we may want to remove because they
   are not common in written English, such as LEMME and WANNA. Again,
   they are genuine English and should probably be accepted if someone
   guesses them, however they make people groan if they spend a long
   time trying to solve the last few words and end up being shown
   these as the words they missed.
   
3. [ ] **OKAY**: Remember this word as valid when playing future games,
   but do not generate puzzles using it. This is for actual words that
   are too obscure. (E.g., NAIAD, TILAPIA, ANNEAL, YURT). Such words
   might be worth bonus points in the future or perhaps earn hints,
   but they are not required to be known to get "100%" on the puzzle.
   The important point is that generated puzzles are fun for most
   people while accomodating folks with grandiloquent vocabularies.

Note that any words on the **ADD** list should be accepted when
playing, even if the gameboard hasn't been regenerated to include it
as one of the official words to search for. It can be treated the same
as the **OKAY** list.

Words on the **REMOVE** list should (probably) also be accepted as
they have all (so far) been actual English words, just obscure ones.

### Give hints

The last few words can be a pain to solve. This program can now give
hints using `!hint`, but it is currently too easy and needs to be
better balanced. It should be discouraged or even forbidden until the
player truly needs it.

  * [x] Give hints by progressively revealing letters of the longest
        remaining word.

	```
	Your guess: !hint
	ABE_____ (8 letters)
	```

  * [ ] Balance hints. Maybe charge for them and if the user doesn't
        have enough points they can't get it? Or use a timer? Or maybe
        randomly offer a hint when they quit if they happen to
        "MATCH", like in pinball — except in this case we want to
        encourage novices so, the less points you have the more likely
        you are to match?

  * [ ] Start out with more subtle hints. For example, _“The most
	common starting letter for the words remaining is 'R'”_ or _“There
	are 3 'R' words, 2 'S' words, and 1 'T' word.”_

  * [ ] Another way to provide hints would be to show them along with
	the found words list (`!s`) using underscores. This would work
	especially well if the found words are already printing to the
	side of the honeycomb. (See other todo item.)

	1. First hint: In the "found words" list, show unfound words using
	   underscores.

		`ABEYANCE  BAOBAB  _______  ______  _____`

	1. Second hint: Fill in the first letter of the longest remaining word.

		`ABEYANCE  BAOBAB  C______  ______  _____`

	1. Fill in the first letter of all remaining words.

		`ABEYANCE  BAOBAB  C______  B_____  N____`

	1. Fill in the second letter of the longest remaining word. 

		`ABEYANCE  BAOBAB  CA_____  B_____  N____`

	1. Fill in the second letter of all remaining words. 

		`ABEYANCE  BAOBAB  CA_____  BA____  NA___`

	1. Fill in third letter of the longest remaining word. 

		`ABEYANCE  BAOBAB  CAY____  BA____  NA___`

	1. et cetera

		`ABEYANCE  BAOBAB  CAY____  BAB___  NAB__`

	1. et cetera

		`ABEYANCE  BAOBAB  CAYE___  BAB___  NAB__`

	1. et cetera

		`ABEYANCE  BAOBAB  CAYE___  BABO__  NABO_`

### libreadline

The user should be able to hit the up arrow to go back in the history
and correct mistakes.

### Show encouragement

Cause, why not?

* [x] “GENIUS LEVEL ACHIEVED: You have found 50% of the hidden words! When
  you quit, any remaining words will be listed.”

* [x] “SUPERBRAIN LEVEL ACHIEVED: You found 85% of the words! You've
  earned a free HINT. Use '!HINT' when stuck.”

* [ ] “ERUDITION BONUS: We didn't expect people to know that word. You get
  one free hint. Use !HINT when stuck.”

### Use "fancy" terminal escape sequences?

* Currently this program runs the same whether on a teletypewriter or
a video terminal. Full screen ncurses would be too much, but it might be
enhanced a bit by

* [ ] the judicious use of bold and reverse color. 

* [ ] Maybe — if we want to go _crazy_ — we could show a one-line ASCII
  animation using carriage-return without newline.

### Dictionary

* [ ] Add !w to look up a word in a dictionary, if dict is installed.

### Are Döppelgangers a problem?

  * [ ] Investigate and maybe remove 

A quick check for identical pangrams (two or more puzzles that have
different center letters but result in the same pangram) shows that
they are not rare. Theoretically, every single letter in a pangram
could be used in the center, generating 7 different puzzles. 

Is this a genuine problem? Due to the center letter restriction,
sometimes the rest of the words can be very different. What's the
appropriate measure if the set of answers is too similar between
puzzles? If they are too similar, which one should be kept?

  * [x] Create a table of Döppelgangers

  For the 3099 puzzles being generated as of 2025:

  | Döppelganger Number | Num Pangrams | Num Puzzles |
  |--------------------:|-------------:|------------:|
  | Unique            1 |          411 |         411 |
  | Twins             2 |          383 |         766 |
  | Triplets          3 |          257 |         771 |
  | Quadruplets       4 |          183 |         732 |
  | Quintuplets       5 |           63 |         315 |
  | Sextuplets        6 |           15 |          90 |
  | Septuplets        7 |            2 |          14 |

  That shows 411 of the puzzles have a unique pangram. There are two
  pangrams which use every single letter in the center. Of the 3099
  puzzles, there are only 1314 pangrams. Simply considering them
  "duplicates" and throwing them out might be problem.

* To generate the table in the future, one can use:

  <!-- Single backtick instead of three so it wraps on the screen -->
  `grep -h -B3 '"pangram": true' data/*.json  | grep word | sort | uniq -c | cut -c-10 | sort -n | uniq -c | awk '{printf("|%4d |%3d |%5d |\n", $2, $1, $1*$2)}'`

* To see which files are the n-tuplets:

  `grep -B3 '"pangram": true' data/*.json  | grep word | sort -k3 | awk '{ $1=substr($1, 6, 7) ; if (old != $3) {print count "\t" files; count=1; files=$1; old=$3;} else {count++; files=files "\t" $1;}} END { print count "\t" files; }' | sort -n `

  the last five lines of that are:

  ```
  6 ECFLORU FCELORU LCEFORU OCEFLRU RCEFLOU UCEFLOR
  6 ECIKLNR ICEKLNR KCEILNR LCEIKNR NCEIKLR RCEIKLN
  6 EFILNTY FEILNTY IEFLNTY LEFINTY NEFILTY TEFILNY
  7 CEHINOR ECHINOR HCEINOR ICEHNOR NCEHIOR OCEHINR RCEHINO
  7 INOPRTU NIOPRTU OINPRTU PINORTU RINOPTU TINOPRU UINOPRT
  ```

  * [x] Make a tool to compare twin puzzles. 
  
    ```
    $ ./utils.py cmp gcinotv icgnotv
	data/GCINOTV.json: 40
	data/ICGNOTV.json: 48
	    Words in both: 37
	          Overlap: 92.50%
    ```
	
    Of the 40 words in `GCINOTV`, only three of them are not in
    `ICGNOTV` for 92.5% overlap. Clearly a player would find one of
    them redundant. The latter has more unique words (11), but more
    words is not always better. Is there a programmatic way to choose
    which should be kept?

  * [ ] Make a tool to compare multiple puzzles. 
  
    ```
    $ ./utils.py cmp AIMNOTV IAMNOTV NAIMOTV OAIMNTV TAIMNOV MAINOTV

    ??? output might be number of unique words or perhaps a histogram
	??? counting the number of words which were found in n different puzzles.
    ??? But is that useful? 
	```
	
	The real metric is, will people feel like they are playing a
	different puzzle or will it be deja vu? Perhaps if more than 50%
	of the words are unique it's okay? 

  * [ ] Maybe Döppelgangers is the wrong way to look at this. Make a
        tool to count up the occurrences of each word over *all*
        puzzles. Maybe a puzzle which has a lot of very common words
        should be discarded regardless of whether it has a unique
        pangram?

