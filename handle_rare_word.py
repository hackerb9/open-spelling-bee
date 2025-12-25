'''Used by play_puzzle to give a reasonable response when the player
guesses a word that is too rare (e.g., "ABATTOIR" is ranked as 50) or
is in a disallowed category (e.g., "BOJANGLES" is in Proper Names).

(Note: See the mkscowl script for where we choose what categories are
accepted and at what rank. Eventually, that will be moved into params.py.
As of 2025, we allow {english,american}-words ≤ 35.)

'''

import utils
from utils import pfill, s

import random

def handle_rare_word(word, player):
    '''Respond to a word that is in a SCOWL wordlist, but it is not common
    enough to accept in the default categories (american,english-words).

    How we respond depends upon both the category and rank. Note that some
    words are in more than one category with possibly different ranks.
    (E.g., english-upper.50: Yucatan. english-words.95: yucatan).

    If the category is 'english-words' then, depending on the rank (10
    being most common, 95 being least) we may prompt them to save it in the
    custom dictionaries dict-okay.txt or dict-add.txt. 
    (TODO: Allow 'american-words' for "airfoil", "alphabetize", etc)

    CATEGORIES:
	ACCEPTABLE:
        {english,american}-words
        {australian,british,canadian}-words
        special-hacker

	UNACCEPTABLE:
        *-{abbreviations,contractions,proper-names,upper}
        special-roman-numerals

        NONSTANDARD:   # Uniquely contains "accurst", "gage", "nite", "zombi"
        *variant_{1,2,3}-words   

        IGNORABLE:
        british_z-words			# ⊂ (American ∪ British)
    '''

    matching_wl = utils.is_in_scowl(word)
    if not matching_wl: return 

    # Is it a common word in a different type of english? ('color', 'bunyip')
    unusual_category = [ wl.category for wl in matching_wl
                         if wl.rank <= 35 and
                         '-words' in wl.category and
                         not 'variant' in wl.category ]
    if unusual_category:
        # Matches british-words, australian-words, or similar
        # XXX maybe give specific response for Britishisms?
        print(f'Acceptable in {", ".join(unusual_category)}')
        return

    # Is the word most commonly a disallowed category? (Try 'USA', 'maths')
    equally_common_cats = [ wl.category for wl in matching_wl
                            if wl.rank == matching_wl[0].rank ]
    if 'english-words' not in equally_common_cats:
        disallowed_cats = [ cat for cat in equally_common_cats
                            if ('-abbreviations' in cat or
                                '-contractions' in cat or
                                '-proper-names' in cat or
                                '-roman-numerals' in cat or
                                '-upper' in cat) ]
        if disallowed_cats:
            matched = matching_wl[0].matches[0]
            if len(disallowed_cats) == 1:
                if '-abbreviations' in disallowed_cats[0]:     # YMCA
                    print(f'Sorry, abbreviations like "{matched}" are NG.')
                elif '-contractions' in disallowed_cats[0]:    # ain't
                    print('Sorry, contractions aren\'t allowed.')
                elif '-proper-names' in disallowed_cats[0]:    # Alex
                    print(f'Sorry, "{matched}" looks like a proper name.')
                elif '-roman-numerals' in disallowed_cats[0]:  # xviii
                    print('Sorry, Roman numerals are not words.')
                elif '-upper' in disallowed_cats[0]: 	       # January
                    print(f'Sorry, "{matched}" is capitalized.')
                else:
                    print(f'Sorry, {disallowed_cats[0]} is not allowed.')
            else:
                print(f'Sorry, {", ".join(disallowed_cats)} are not allowed.')
            return

    # Is the word acceptable in Hacker jargon? ('bletch').
    if [ wl for wl in matching_wl if wl.category == 'special-hacker' ]:
        print(f'Use !okay to accept this hacker jargon as a bonus word.')
        return

    # Now check if it matched in english-words but with rank >35  
    for wl in matching_wl:
        if wl.category == 'english-words':
            player.rare_words[wl.rank].append(word)
#            print (wl.rank)
            if wl.rank <= 35:
                pfill(f'Hunky dory: "{word}" looks swell to me! This routine shouldn\'t have been called.')
                return
            if wl.rank == 40:
                explication = [f'To make the puzzle completable, I only expect the most commonplace words and "{word}" wasn\'t in my list.',
                               f'Use !add if everyone should be required to find "{word}" in future puzzles.',
                               f'If "{word}" is a good word but not good enough that it should be required to solve the puzzle, use !okay to allow a bonus for finding it.'
                               #f'Otherwise, do nothing and enjoy knowing you have an above average vocabulary.'
                               ]
                pfill(f"That's a nice one I should have thought of. {random.choice(explication)}")
                return
            elif wl.rank == 50:
                pfill(f'Oh! I hadn\'t thought of "{word}". Use !okay to mark it as a bonus word.')
                return
            elif wl.rank == 55:
                pfill(f'Hmm. That is not one of the typical English words I am thinking of. Do people deserve a bonus for finding "{word}"? If so, use !okay.')
                return
            elif wl.rank == 60:
                pfill(f'I\'m dubious about "{word}". If it is a word one should be proud of knowing, please use !okay to mark it as acceptable.')
                return
            elif wl.rank == 70:
                boring=['pedestrian', 'quotidian', 'everyday', 'mundane']
                pfill(f'You have an impressive vocabulary! But I was told "{word}" was too unusual to accept. Do you see any {random.choice(boring)} words?')
                return
            elif wl.rank == 80:
                wacky=['abstruse', 'esoteric', 'recondite', 'obscure']
                pfill(f'"{word}" is a bit too {random.choice(wacky)} for me.')
                return
            else: # wl.rank <= 95:
                # CONTEMNIBLE SCAPEGRACE
                uhno=[f'Sorry, "{word}" is inadmissable.',
                      f'If I had eyes, I\'d be rolling them right now.',
                      f'I think we both know "{word}" should not be accepted.',
                      f'You can do better than "{word}".']
                pfill(random.choice(uhno))
                return
        
    # If we get here, the word was not in the english-words category.

    # Handle rank >35 from australian, british, canadian-words
    # Is it an uncommon word in a different type of english?
    # Try 'greyish'
    unusual_category = [ wl.category for wl in matching_wl
                         if wl.rank > 35 and
                         '-words' in wl.category and
                         not 'variant' in wl.category ]
    if unusual_category:
        # Matches british-words or similar
        pfill(f'Less common word "{word}" found in {", ".join(unusual_category)}. Maybe use !okay.')
        # XXX maybe give more specific advice here
        return

    # Is the word most commonly a variant spelling ('nite', 'gage')
    variant_cats = [ wl.category for wl in matching_wl
                     if wl.rank == matching_wl[0].rank and
                     'variant' in wl.category ]
    if variant_cats:
        print(f'Sorry, that spelling is not allowed here.')
        print
        return

    # All categories accounted for above, but just in case...
    print(f'Seems a bit sketchy....')
    print(matching_wl)
    print("If you're sure, use !okay to allow it.")
    print

