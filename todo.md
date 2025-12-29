## To do

### Consider banning the letter 'S'

NYT never allows puzzles with the letter S in order to prevent
plurals. Actually, there was an exception on March 12, 2025 `FLOSUAB`
and a few others since then. We do not need this restriction since we
already already attempt to cut out puzzles that have lots of plurals.
See generate_puzzles.py.a

### Maybe allow variants

"Variants" of words are stored in separate files. It is not clear what
that means in terms of word frequency since they still have the
numeric suffixes. For example, "yogurt" is not found in
`english-words.*`, but it is in `variant_1-words.35`:

``` console
$ egrep 'y.*g.*rt$' *-words.35
```

|            | Primary | Variant 1         | Variant 2         |
|------------|---------|-------------------|-------------------|
| English    |         | yogurt            | yoghurt, yoghourt |
| American   | yogurt  |                   |                   |
| Australian | yoghurt | yogurt            | yoghourt          |
| British    | yogurt  | yoghurt, yoghourt |                   |
| Canadian   | yogourt | yogurt, yoghurt   | yoghourt          |

### Deal with too many rejected words

Ever since we switched from TWL06.txt to SCOWL's english-words.35, too
many words are being refused. Example: IACLNOV:

    avian, iconic, laconic, clinician, cilia, loci, aioli, cavil,
    convivial, cannoli, oilcan, voila, parry, aurora, pyro, purl,
	parlay, orally, aurally, acacia, conic, niacin, lanolin

Of course, we can't go back to TWL since it jumbles up the common
words with grotesqueries that aren't even in the Oxford English
Dictionary, (e.g., "NAOI", "ILIA") and hyper-specific terms of art
("CONCANAVALIN")

SCOWL categorizes the words I found as less frequently used, primarily
english-words.50 (the top 50% of English words). While "pyro" and
"cannoli" may be questiionable, it certainly feels wrong to not accept
a common word like "aurora".

<details><summary>Which SCOWL word lists contain what</summary>
<ul>

  * 40: clinician, convivial, orally
  * 50: acacia, aurally, avian, cavil, cilia, conic, laconic, lanolin,
    loci,niacin, parlay, parry, purl
  * 55: iconic, oilcan
  * 60: aurora
  * 70: cannoli
  * 80: pyro

</ul></details>

  * [x] Should we change the cut off from 35 to 50 when creating
        puzzles? No. It adds in too many words which we can't expect
        people to know. Here's what would be added for each wordlist.
		
<details><summary>What else the wordlists brang in</summary><ul>

* 40: _[none]_
* 50: anion, cocci, loci, viol, viva, vocalic
* 55: avionic, ciao, lilo, lino, vino
* 60: anionic, ilia, lanai, nonclinical, villi
* 70: aalii, acini, alcaic, aloin, ... _[40 words elided]_ ..., vicinal, vina, vinic
* 80: accoil, acinic, ... _[50 words elided]_ ..., vinca, vivo, vocalion, volcanian

</ul></details>

#### Therefore: No one scowl dictionary is best

We need custom dictionaries, created by everyone who plays the game.

* [ ] `!ok` should add words to a user dictionary for acceptance, but
      not game creation.

* [x] `!scowl` should look up words in SCOWL and show the frequency.

* [ ] `!upload` should upload the custom wordlist to github.io so that
      users can share their dictionaries and our default wordlists
      will become more sensible over time.

Hackerb9a has noticed that most of the custom words he's adding to
"dict-okay" are already in scowl.50 or scowl.40. If the game would
simply accept those word lists, very few words would need to be added
manually.

* [ ] Give player bonuses for words which are not in the generating
  dictionary but are valid in more recondite sources. 
  * [x] Check custom user dict-*.txt, 
  * [x] more scowl, upto and including english-words.50
  * [ ] TWL
  * [ ] local dictd
  * [ ] online dictd
  
* [x] At 70% score, allow players to convert earned bonuses into hints.

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

* [ ] Stem words. Perhaps what gets players annoyed is when they have
      to inflect every word: WAGE, WAGED, WAGING, WAGGLE, WAGGLED,
      WAGGLING, ...
  
  * `VDEIPWR`: view, viewer, viewed, preview, previewer, previewed,
    review, reviewer, reviewed, dive, diver, dived, peeve, peeved, ...
	(uniqueness is quite low at 0.36)

  * [ ] generate-puzzles.py:make_puzzles()
		More reasons for is_valid = False.

	* [x] Count `-S` pairs (simple plural)

	* [x] Count `-ING` pairs (present participle and gerundive)

	* [x] Count `-ED` pairs (preterite == simple past tense). Test with DEFLOUY.
	* [ ] Find the root words and ensure we have a sufficient number: 
		  WAGE, WAGED, WAGING == 1 stem. Test with `MDELRUY`.

### Estimate number of compound words. 

  * [ ] Split words into two halves and check if they are valid words.
        "Ringworm is neither a 'ring' nor a 'worm'. It is a fungus."


### Place found words to the side of the grid

* [ ] While probably distracting if it was always shown, it may be
  nice to sometimes have the words the user has found printed to the
  side of the puzzle. The list probably should be printed in columns
  so as to maximize the distance from the puzzle.

### Commands to add words to user lists

The user should be able to quickly add words to a list when they
come up during play.

There should be at least three word lists.

1. [ ] **!ADD**: Add this word to the dictionary used to generate puzzles in
   the future. (E.g., AURORA, LINGUINI, FALAFEL, ALFALFA, UNICYCLING
   are not in the current default dictionary.)
   
2. [ ] **!REMOVE**: This word should be on the "stoplist" so it will not be
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
   
3. [ ] **!OKAY**: Remember this word as valid when playing future games,
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


### Use "fancy" terminal escape sequences?

* Currently this program runs the same whether on a teletypewriter or
a video terminal. Full screen ncurses would be too much, but it might be
enhanced a bit by

* [ ] the judicious use of bold and reverse color. 

* [ ] Maybe — if we want to go _crazy_ — we could show a one-line ASCII
  animation using carriage-return without newline.

* [ ] Some people would like the center letter to be bold or reverse.


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

### Hapax Legomena

Nonce words are perfectly crommulent.

[hapax]: https://archive.examiningtheoed.com/oed.hertford.ox.ac.uk/main/content/view/402/450/ "Discussion of Hapax Legomena in the Oxfored English Dictionary"
				  
### Get rid of mkscowl

mkscowl script currently converts the multitude of scowl files to a
single homogeneous file.

 * [ ] Instead play_puzzle.py ought to search the scowl dictionaries
       of a certain frequency level (set in params.py?) instead of
       hardcoding it to ≤35 with bonus ≤50.



## DONE. 

Delete me eventually.

### Match accented characters

 * [x] If the user types "pinata", then it should match _piñata_ in a
	   wordlist. To test, try _canapé_ which is in Scowl only accented.

### Dictionary

* [x] Add !dict to define a word in a dictionary, if dict is installed.

* [x] Add !match to look up the headword in a dictionary, using both
      SCOWL and dict.

### Show encouragement

Cause, why not?

* [x] “ERUDITION BONUS: We didn't expect people to know that word.
  You've earned a bonus!”

* [x] “AMAZING LEVEL ACHIEVED: You have found 50% of the hidden words! When
  you quit, any remaining words will be listed.”

* [x] “GENIUS LEVEL ACHIEVED: You have found 70% of the words. You can
  now convert your bonus points into hints, if you'd like.

* [x] “SUPERBRAIN LEVEL ACHIEVED: You found 85% of the words! You've
  earned a free HINT. Use '!HINT' when stuck.”

### Remove Britishisms

* [x] People don't like having to do both "defense" and "defence". 

