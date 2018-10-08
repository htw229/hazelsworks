

# REGULAR_CONJUGATES = [
#     {'ending': [''], 'suffix': ['s'], 'replace': False}, # for purals and verbs, always try just adding s
#
#     # PLURALS
#     {'ending': ['s', 'sh', 'ch', 'x'], 'suffix': ['es'], 'replace': False},
#     {'ending': ['z'], 'suffix': ['zzes'], 'replace': True},
#     {'ending': ['s'], 'suffix': ['sses'], 'replace': True},
#     {'ending': ['y'], 'suffix': ['ies'], 'replace': True},
#     {'ending': ['f', 'fe'], 'suffix': ['ves'], 'replace': True},
#     {'ending': ['o'], 'suffix': ['oes'], 'replace': True},
#     {'ending': ['us'], 'suffix': ['i'], 'replace': True},
#     {'ending': ['is'], 'suffix': ['es'], 'replace': True},
#     {'ending': ['on'], 'suffix': ['a'], 'replace': True},
#     {'ending': ['um'], 'suffix': ['a'], 'replace': True},
#     {'ending': ['ix', 'ex'], 'suffix': ['ices', 'ixes', 'exes'], 'replace': True},
#
#     # POSSESSIVE
#     {'ending': [''], 'suffix':[r"'s"], 'replace': False},
#     {'ending': ['s'], 'suffix':[r"'"], 'replace': False},
#
#     # ADJECTIVES
#     {'ending': [''], 'suffix': ['al', 'y', 'ful', 'ous', 'ious', 'ic'], 'replace': False},
#     {'ending': ['e'], 'suffix': ['al', 'y'], 'replace': True},
#     {'ending': ['y'], 'suffix': ['iful', 'ous', 'ious', 'ic'], 'replace': True},
#     {'ending': [r'([aeiou])([^aeiou])'], 'suffix': [r'\1\2\2al', r'\1\2\2y', r'\1\2\2ous', r'\1\2\2ious', r'\1\2\2ic'], 'replace': True}, # double ending consonant if vowel-consonant
#
#     # ADVERBS
#     {'ending': [''], 'suffix': ['ly'], 'replace': False},
#     {'ending': ['y'], 'suffix': ['ily'], 'replace': True},
#     {'ending': ['le'], 'suffix': ['ly'], 'replace': True},
#     {'ending': ['ic'], 'suffix': ['ally'], 'replace': False},
#     {'ending': [''], 'suffix': ['edly', 'ingly'], 'replace': False},
#     {'ending': ['e'], 'suffix': ['edly', 'ingly'], 'replace': True},
#
#     # VERBS
#     {'ending': [''], 'suffix': ['ed', 'ing'], 'replace': False},
#     {'ending': ['e'], 'suffix': ['ed', 'ing'], 'replace': True},
#     {'ending': [r'([aeiou])([^aeiou])'], 'suffix': [r'\1\2\2ed', r'\1\2\2ing'], 'replace': True}, # double ending consonant if vowel-consonant
# ]

# necessary if more than one word only
POSSESSIVES = [
    # POSSESSIVE
    {'ending': [''], 'suffix': [r"'s"], 'replace': False, },
    {'ending': ['s'], 'suffix': [r"'"], 'replace': False, },
]

PLURALS = [
    # PLURALS
    {'ending': ['[^s]'], 'negativeending': ['(s|[^aeiou]y)'], 'suffix': ['s'], 'replace': False,},
    {'ending': ['(?<=[aeiou])s', '(?<=[aeiou])sh', '(?<=[aeiou])ch', '(?<=[aeiou])x'], 'suffix': ['es'],
     'replace': False, },
    {'ending': ['z'], 'suffix': ['zzes'], 'replace': True, },
    {'ending': ['s'], 'suffix': ['sses'], 'replace': True, },
    {'ending': ['y'], 'suffix': ['ies'], 'replace': True, },
    {'ending': ['f', 'fe'], 'suffix': ['ves'], 'replace': True, },
    {'ending': ['o'], 'suffix': ['oes'], 'replace': True, },
    {'ending': ['is'], 'suffix': ['es'], 'replace': True, },
    {'ending': ['ix', 'ex'], 'suffix': ['ices', 'ixes', 'exes'], 'replace': True, },
]


# test deleting uncommon ones
REGULAR_CONJUGATES = [
     # for purals and verbs, always try just adding s

    # NOUNS
    {'ending': ['[^y]'], 'suffix': ["ness"], 'replace': False,},
    {'ending': ['(?<=[^aeiou])y'], 'suffix': ["iness"], 'replace': True,},
    {'ending': ['ent'], 'suffix': [r"ence"], 'replace': True,},

    # ADJECTIVES
    {'ending': ['[^aiouy]'], 'suffix': ['y'], 'replace': False,},
    # {'ending': ['e'], 'suffix': ['y'], 'replace': True,},

    # TODO: this and one below aren't working; why?
    {'ending': [r'(?P<v>[aeiou])(?P<c>[^aeiou])'], 'suffix': [r'\g<v>\g<c>\g<c>y'], 'replace': True,}, # double ending consonant if vowel-consonant
    {'ending': ['[^ey]'], 'suffix': ['ful', 'ious', 'ic'], 'replace': False,},
    {'ending': ['[^e]'], 'suffix': ['ous'], 'replace': False,},
    {'ending': ['[^e]'], 'suffix': ['al', 'y'], 'replace': False,},
    {'ending': ['ion'], 'suffix': ['ious',], 'replace': True,},
    {'ending': ['(?<=[ct])y'], 'suffix': ['iful', 'ous', 'ious', 'ic'], 'replace': True,},

    # ADVERBS
    {'ending': ['[^y]'], 'suffix': ['ly'], 'replace': False,},
    {'ending': ['y'], 'suffix': ['ily'], 'replace': True,},
    {'ending': ['le'], 'suffix': ['ly'], 'replace': True,},
    {'ending': ['ic'], 'suffix': ['ally'], 'replace': False,},

    # VERBS
    {'ending': ['[^s]'], 'suffix': ['s'], 'replace': False,},
    {'ending': [''],
     'negativeending': ['([ey]|[aeiou][^aeioul]|[aeiou]{2,})'], # losing too many by overgeneralizing with vowel-non-vowel here?
     'suffix': ['ed', 'ing'], 'replace': False,
     },
    {'ending': ['[aeou]y'], 'suffix': ['ed', 'ing'], 'replace': False,},
    {'ending': ['e'], 'suffix': ['ed', 'ing'], 'replace': True,},
    {'ending': [r'([aeiou])([^aeiou])'], 'suffix': [r'\1\2\2ed', r'\1\2\2ing'], 'replace': True,}, # double ending consonant if vowel-consonant
]


# only apply to created conjugates
# (many of these can be valid in some circumstances)
DISALLOWED_ENDINGS = [
    r'(\w)\1+', #2 or more of the same letter
    r'[^aeiou]ys',
]



SUFFIX_IGNORE_PATTERN = r'\[\]\s'


PREPOSITION_LIST = [
    'to',
    'up',
    'out',
    'of',
    'with',
    'over',
    'it',
    'that',
    'from',
    'a',
    'an',
    'the',
    'this',
    'the',
]

OPTIONAL_WORDS_LIST = [
    'a',
    'an',
    'the',
]

#TODO: add possessive markup [possessive]=his, hers, my, your, our, [word]'s
# TODO: don't make a and the optional

MARKUP = {
    'number': ['\d{1,2}', '\d{1,2}st', '\d{1,2}nd', '\d+th', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth',
                 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
                 'eighteenth', 'nineteenth', 'twentieth', 'thirtieth', 'fourtieth', 'fiftieth', 'hundredth',
                 'thousandth', 'millionth'],
    'month': ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec', 'january',
                'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
                'december'],
    'me': ['him', 'her', 'them', 'me', 'us'],
    'mine': ['his', 'hers', 'theirs', 'mine', 'ours'],
    'my': ['his', 'her', 'their', 'my', 'our',],
    'I': ['he', 'she', 'they', 'I', 'we',], # TODO: not working - see 100
    'possessive': ['my', 'our', 'your', 'his', 'her', 'its', r"(?<='s)"],
    'the': ['the', 'a', 'an', 'that', 'this', 'what', 'which',],
    'noun_preceding': ['my', 'our', 'your', 'his', 'her', 'its', r"(?<='s)", 'the', 'a', 'an', 'that', 'this', 'what', 'which',],
}


#TODO: add british spellings
# TODO:  add british/american variable word endings
    # TODO: add negatives? (isn't, weren't, don't, can't, couldn't, shouldn't etc) add contractions? (is -> 's, 's not, s'not)
    # TODO: make curly quotes and apostrophes regular?
# TODO: add a 'must have x word nearby' - for example "back up" needs to have some kind of car term nearby

# british transformations
VARIABLE_WORD_ENDINGS=[("ence", "ense"),("ogue", "og"),("yse", "yze"),("ize", "ise"),("our", "or"),("er", "re")]

# too much work for very little use? add replacing pronouns in if needed
#
# PRONOUNS = [
#     ['i', 'we', 'you', 'you all', 'she', 'he', 'they'],
#     ['my', 'your', '']
# ]

PROTECTED_CONJUGATES =[
    ['do', 'did', 'doing', 'does', 'done', 'do not', 'will not', "don't", "doesn't", "won't", "didn't"],
    ['is', 'been', 'are', 'am', 'be', 'being', 'was', 'were', "aren't", "isn't", "I'm", "I'm not"],
    ['comes', 'came', 'come', 'coming'],
    ['give', 'given', 'gave', 'giving', 'gives'],
    ['having', 'had', 'have', 'has'],
]


IRREGULAR_CONJUGATES =[
# irregular verbs
    ['abides', 'abiding', 'abide', 'abode'],
    ['alighting', 'alit', 'alights', 'alight'],
    ['arise', 'arisen', 'arose', 'arises', 'arising'],
    ['awaking', 'awakes', 'awoken', 'awake', 'awoke'],
    ['bears', 'bore', 'bearing', 'bear', 'born', 'borne'],
    ['beating', 'beat', 'beaten', 'beats'],
    ['become', 'becoming', 'became', 'becomes'],
    ['befell', 'befall', 'befalls', 'befalling', 'befallen'],
    ['begin', 'began', 'begun', 'begins', 'beginning'],
    ['beholding', 'beheld', 'beholds', 'behold'],
    ['bends', 'bend', 'bent', 'bending'],
    ['bereave', 'bereaving', 'bereaves', 'bereft'],
    ['beseech', 'besought', 'beseeching', 'beseeches'],
    ['bets', 'betting', 'bet'],
    ['bidden', 'bids', 'bidding', 'bid', 'bade'],
    ['bidding', 'bids', 'bid'],
    ['bind', 'bound', 'binds', 'binding'],
    ['biting', 'bite', 'bites', 'bit', 'bitten'],
    ['bleed', 'bled', 'bleeds', 'bleeding'],
    ['blows', 'blowing', 'blew', 'blown', 'blow'],
    ['breaking', 'broken', 'break', 'breaks', 'broke'],
    ['breed', 'breeds', 'breeding', 'bred'],
    ['bringing', 'brought', 'bring', 'brings'],
    ['broadcasting', 'broadcasts', 'broadcast'],
    ['building', 'built', 'builds', 'build'],
    ['burn', 'burnt', 'burning', 'burns'],
    ['bursts', 'bursting', 'burst'],
    ['busting', 'bust', 'busts'],
    ['buys', 'bought', 'buying', 'buy'],
    ['casts', 'cast', 'casting'],
    ['catch', 'catching', 'catches', 'caught'],
    ['chides', 'chide', 'chid', 'chidden', 'chiding'],
    ['choose', 'chose', 'chooses', 'choosing', 'chosen'],
    ['cleave', 'clove', 'cleft', 'cleaving', 'cleaves', 'cloven', 'cleft'],
    ['clung', 'clings', 'cling', 'clinging'],
    ['clothes', 'clothe', 'clad', 'clothing'],
    ['costs', 'costing', 'cost'],
    ['creeping', 'creeps', 'creep', 'crept'],
    ['cutting', 'cut', 'cuts'],
    ['dealt', 'deals', 'deal', 'dealing'],
    ['digging', 'digs', 'dig', 'dug'],
    ['draw', 'drawn', 'draws', 'drawing', 'drew'],
    ['dreamt', 'dreams', 'dream', 'dreaming'],
    ['drunk', 'drinks', 'drank', 'drink', 'drinking'],
    ['drove', 'driven', 'drive', 'drives', 'driving'],
    ['dwells', 'dwell', 'dwelt', 'dwelling'],
    ['eat', 'ate', 'eaten', 'eating', 'eats'],
    ['fallen', 'falling', 'falls', 'fell', 'fall'],
    ['farting', 'farts', 'fart'],
    ['feeding', 'fed', 'feed', 'feeds'],
    ['feel', 'feeling', 'felt', 'feels'],
    ['fights', 'fought', 'fight', 'fighting'],
    ['finding', 'finds', 'find', 'found'],
    ['fits', 'fitting', 'fit'],
    ['fleeing', 'flees', 'fled', 'flee'],
    ['flung', 'fling', 'flinging', 'flings'],
    ['flies', 'flying', 'flew', 'flown', 'fly'],
    ['forbid', 'forbidden', 'forbade', 'forbidding', 'forbids'],
    ['forecasting', 'forecasts', 'forecast'],
    ['forget', 'forgets', 'forgetting', 'forgot', 'forgotten'],
    ['forgiven', 'forgives', 'forgive', 'forgiving', 'forgave'],
    ['forsake', 'forsaking', 'forsaken', 'forsook', 'forsakes'],
    ['frozen', 'freezing', 'freezes', 'froze', 'freeze'],
    ['gainsay', 'gainsaid', 'gainsaying', 'gainsays'],
    ['get', 'gets', 'getting', 'got'],
    ['girt', 'gird', 'girds', 'girding'],
    ['gone', 'went', 'goes', 'go', 'going'],
    ['graves', 'graven', 'grove', 'graving', 'grave'],
    ['grows', 'grow', 'grew', 'grown', 'growing'],
    ['hanging', 'hung', 'hangs', 'hang'],

    ['hearing', 'hear', 'hears', 'heard'],
    ['heave', 'heaves', 'hove', 'heaving'],
    ['hew', 'hews', 'hewing', 'hewn', 'hewed'],
    ['hid', 'hiding', 'hide', 'hides', 'hidden'],
    ['hitting', 'hit', 'hits'],
    ['held', 'holding', 'holds', 'hold'],
    ['hurt', 'hurts', 'hurting'],
    ['inlaid', 'inlaying', 'inlays', 'inlay'],
    ['input', 'inputs', 'inputting'],
    ['kept', 'keeps', 'keep', 'keeping'],
    ['knelt', 'kneeling', 'kneel', 'kneels'],
    ['knits', 'knit', 'knitting'],
    ['knows', 'knowing', 'knew', 'know', 'known'],
    ['lading', 'lade', 'laden', 'lades', 'laded'],
    ['lay', 'lays', 'laid', 'laying'],
    ['led', 'lead', 'leading', 'leads'],
    ['lean', 'leans', 'leaning', 'leant'],
    ['leap', 'leaps', 'leaping', 'leapt'],
    ['learning', 'learnt', 'learns', 'learn'],
    ['leaving', 'leave', 'leaves', 'left'],
    ['lending', 'lend', 'lends', 'lent'],
    ['let', 'lets', 'letting'],
    ['lies', 'lay', 'lain', 'lie', 'lying'],
    ['light', 'lit', 'lighting', 'lights'],
    ['loses', 'lost', 'lose', 'losing'],
    ['made', 'make', 'makes', 'making'],
    ['meant', 'meaning', 'means', 'mean'],
    ['met', 'meet', 'meeting', 'meets'],
    ['mistake', 'mistook', 'mistakes', 'mistaken', 'mistaking'],
    ['mowing', 'mowed', 'mows', 'mow', 'mown'],
    ['partakes', 'partake', 'partook', 'partaking', 'partaken'],
    ['paid', 'pays', 'paying', 'pay'],
    ['plead', 'pleads', 'pleading', 'pled'],
    ['putting', 'puts', 'put'],
    ['quits', 'quit', 'quitting'],
    ['reading', 'reads', 'read'],
    ['rends', 'rend', 'rending', 'rent'],
    ['rid', 'rids', 'ridding'],
    ['riding', 'ride', 'rode', 'rides', 'ridden'],
    ['rings', 'ring', 'rung', 'ringing', 'rang'],
    ['rises', 'risen', 'rose', 'rising', 'rise'],
    ['run', 'ran', 'running', 'runs'],
    ['sawed', 'sawn', 'saws', 'saw', 'sawing'],
    ['says', 'say', 'saying', 'said'],
    ['see', 'seen', 'seeing', 'saw', 'sees'],
    ['seeks', 'seeking', 'seek', 'sought'],
    ['selling', 'sold', 'sells', 'sell'],
    ['send', 'sending', 'sends', 'sent'],
    ['sets', 'set', 'setting'],
    ['sews', 'sewn', 'sew', 'sewing', 'sewed'],
    ['shaken', 'shook', 'shaking', 'shake', 'shakes'],
    ['shaven', 'shove', 'shave', 'shaving', 'shaves'],
    ['shorn', 'shearing', 'shears', 'shore', 'shear'],
    ['sheds', 'shedding', 'shed'],
    ['shining', 'shines', 'shine', 'shone'],
    ['shitting', 'shits', 'shit'],
    ['shoeing', 'shod', 'shoes', 'shoe'],
    ['shoots', 'shooting', 'shot', 'shoot'],
    ['showing', 'show', 'showed', 'shows', 'shown'],
    ['shrinking', 'shrunk', 'shrinks', 'shrank', 'shrink'],
    ['shriven', 'shrives', 'shriving', 'shrove', 'shrive'],
    ['shut', 'shutting', 'shuts'],
    ['sang', 'sung', 'sings', 'sing', 'singing'],
    ['sink', 'sinking', 'sank', 'sinks', 'sunk'],
    ['sit', 'sits', 'sitting', 'sat'],
    ['slain', 'slay', 'slaying', 'slew', 'slays'],
    ['sleeps', 'slept', 'sleep', 'sleeping'],
    ['slides', 'slid', 'slide', 'sliding'],
    ['slings', 'slung', 'slinging', 'sling'],
    ['slinking', 'slunk', 'slink', 'slinks'],
    ['slits', 'slit', 'slitting'],
    ['smelt', 'smells', 'smelling', 'smell'],
    ['smitten', 'smite', 'smote', 'smiting', 'smites'],
    ['spoke', 'speak', 'spoken', 'speaks', 'speaking'],
    ['speed', 'sped', 'speeds', 'speeding'],
    ['spelt', 'spell', 'spelling', 'spells'],
    ['spend', 'spends', 'spending', 'spent'],
    ['spilling', 'spilt', 'spills', 'spill'],
    ['spin', 'spins', 'spinning', 'spun'],
    ['spits', 'spat', 'spitting', 'spit'],
    ['split', 'splits', 'splitting'],
    ['spoiling', 'spoilt', 'spoil', 'spoils'],
    ['spreading', 'spreads', 'spread'],
    ['springing', 'spring', 'sprang', 'springs', 'sprung'],
    ['stands', 'stood', 'standing', 'stand'],
    ['stole', 'steal', 'stolen', 'steals', 'stealing'],
    ['stick', 'sticks', 'sticking', 'stuck'],
    ['stings', 'stung', 'sting', 'stinging'],
    ['stank', 'stinking', 'stink', 'stunk', 'stinks'],
    ['strew', 'strews', 'strewed', 'strewn', 'strewing'],
    ['stride', 'strides', 'strode', 'stridden', 'striding'],
    ['striking', 'strikes', 'stricken', 'strike', 'struck'],
    ['strings', 'stringing', 'string', 'strung'],
    ['strives', 'striven', 'strove', 'strive', 'striving'],
    ['sworn', 'swear', 'swears', 'swore', 'swearing'],
    ['sweating', 'sweat', 'sweats'],
    ['swept', 'sweeps', 'sweep', 'sweeping'],
    ['swelled', 'swell', 'swells', 'swollen', 'swelling'],
    ['swam', 'swims', 'swum', 'swim', 'swimming'],
    ['swung', 'swinging', 'swing', 'swings'],
    ['takes', 'taking', 'take', 'took', 'taken'],
    ['teaches', 'taught', 'teaching', 'teach'],
    ['tore', 'tears', 'tearing', 'torn', 'tear'],
    ['telling', 'told', 'tell', 'tells'],
    ['thought', 'think', 'thinking', 'thinks'],
    ['throve', 'thriving', 'thriven', 'thrives', 'thrive'],
    ['throws', 'threw', 'throw', 'thrown', 'throwing'],
    ['thrust', 'thrusts', 'thrusting'],
    ['treading', 'treads', 'trod', 'tread', 'trodden'],
    ['understands', 'understanding', 'understand', 'understood'],
    ['woken', 'wakes', 'woke', 'wake', 'waking'],
    ['way-lay', 'way-laying', 'way-lays', 'way-laid'],
    ['wore', 'wears', 'worn', 'wear', 'wearing'],
    ['wove', 'weaving', 'woven', 'weaves', 'weave'],
    ['weds', 'wedding', 'wed'],
    ['weeps', 'weep', 'wept', 'weeping'],
    ['welcomes', 'welcome', 'welcomed', 'welcoming'],
    ['went', 'wends', 'wending', 'wend'],
    ['wets', 'wetting', 'wet'],
    ['won', 'wins', 'win', 'winning'],
    ['winding', 'wound', 'wind', 'winds'],
    ['withdraws', 'withdrawn', 'withdrawing', 'withdraw', 'withdrew'],
    ['wring', 'wrings', 'wringing', 'wrung'],
    ['wrote', 'writes', 'write', 'written', 'writing'],


# IRREGULAR NOUNS
    ["addendum", "addenda", "addendums"],
    ["aircraft", "aircraft"],
    ["alumna", "alumnae"],
    ["alumnus", "alumni"],
    ["analysis", "analyses"],
    ["antenna", "antennae", "antennas"],
    ["antithesis", "antitheses"],
    ["apex", "apices", "apexes"],
    ["appendix", "appendices", "appendixes"],
    ["axis", "axes"],
    ["bacillus", "bacilli"],
    ["bacterium", "bacteria"],
    ["basis", "bases"],
    ["beau", "beaux", "beaus"],
    ["bison", "bison"],
    ["bureau", "bureaux", "bureaus"],
    ["cactus", "cacti", "cactus", "cactuses"],
    ["château", "châteaux", "châteaus"],
    ["child", "children"],
    ["codex", "codices"],
    ["concerto", "concerti", "concertos"],
    ["corpus", "corpora"],
    ["crisis", "crises"],
    ["criterion", "criteria", "criterions"],
    ["curriculum", "curricula", "curriculums"],
    ["datum", "data"],
    ["deer", "deer", "deers"],
    ["diagnosis", "diagnoses"],
    ["die", "dice", "dies"],
    ["dwarf", "dwarves", "dwarfs"],
    ["ellipsis", "ellipses"],
    ["erratum", "errata"],
    ["faux pas", "faux pas"],
    ["fez", "fezzes", "fezes"],
    ["fish", "fish", "fishes"],
    ["focus", "foci", "focuses"],
    ["foot", "feet", "foot"],
    ["formula", "formulae", "formulas"],
    ["fungus", "fungi", "funguses"],
    ["genus", "genera", "genuses"],
    ["goose", "geese"],
    ["graffito", "graffiti"],
    ["grouse", "grouse", "grouses"],
    ["half", "halves"],
    ["hoof", "hooves", "hoofs"],
    ["hypothesis", "hypotheses"],
    ["index", "indices", "indexes"],
    ["larva", "larvae", "larvas"],
    ["libretto", "libretti", "librettos"],
    ["loaf", "loaves"],
    ["locus", "loci"],
    ["louse", "lice"],
    ["man", "men"],
    ["matrix", "matrices", "matrixes"],
    ["medium", "media", "mediums"],
    ["memorandum", "memoranda", "memorandums"],
    ["minutia", "minutiae"],
    ["moose", "moose"],
    ["mouse", "mice"],
    ["nebula", "nebulae", "nebulas"],
    ["nucleus", "nuclei", "nucleuses"],
    ["oasis", "oases"],
    ["offspring", "offspring", "offsprings"],
    ["opus", "opera", "opuses"],
    ["ovum", "ova"],
    ["ox", "oxen", "ox"],
    ["parenthesis", "parentheses"],
    ["phenomenon", "phenomena", "phenomenons"],
    ["phylum", "phyla"],
    ["prognosis", "prognoses"],
    ["quiz", "quizzes"],
    ["radius", "radii", "radiuses"],
    ["referendum", "referenda", "referendums"],
    ["salmon", "salmon", "salmons"],
    ["scarf", "scarves", "scarfs"],
    ["self", "selves"],
    ["series", "series"],
    ["sheep", "sheep"],
    ["shrimp", "shrimp", "shrimps"],
    ["species", "species"],
    ["stimulus", "stimuli"],
    ["stratum", "strata"],
    ["swine", "swine"],
    ["syllabus", "syllabi", "syllabuses"],
    ["symposium", "symposia", "symposiums"],
    ["synopsis", "synopses"],
    ["tableau", "tableaux", "tableaus"],
    ["thesis", "theses"],
    ["thief", "thieves"],
    ["tooth", "teeth"],
    ["trout", "trout", "trouts"],
    ["tuna", "tuna", "tunas"],
    ["vertebra", "vertebrae", "vertebras"],
    ["vertex", "vertices", "vertexes"],
    ["vita", "vitae"],
    ["vortex", "vortices", "vortexes"],
    ["wharf", "wharves", "wharfs"],
    ["wife", "wives"],
    ["wolf", "wolves"],
    ["woman", "women"],
    ["foot", "feet"],
    ["tooth", "teeth"],
    ["goose", "geese"],
    ["man", "men"],
    ["woman", "women"],
    ["louse", "lice"],
    ["mouse", "mice"],
    ["die", "dice"],
    ["ox", "oxen"],
    ["child", "children"],
    ["person", "people"],
    ["penny", "pence"],
]


# words to ignore when transforming
# includes determiners, pronouns, prepositions, postpositions, particles
PROTECTED_WORDS = ["'gainst", "'long", "'mong, mong, 'mongst", "'neath", "'nough", "a", "a few", "a good few", "a good many", "a little", "a whole 'nother", "a whole nother", "aboard", "about", "above", "absent", "according to", "across", "across from", "adjacent to", "after", "again", "against", "ahead of", "ahind", "all", "all y'all", "alls", "almost all", "along", "along with", "alongside", "alotta", "amid", "amidst", "among", "amongst", "an", "anny", "anoda", "anotha", "anotha'", "another", "any", "any and all", "any ol'", "any old", "any ole", "any-and-all", "anybody", "anyone", "anything", "apart", "apart from", "apropos", "apud", "around", "ary", "as", "as for", "as of", "as per", "as regards", "aside", "aside from", "ask out", "astride", "at", "atop, ontop", "atta", "atween", "aught", "away", "ayond", "back", "back to", "bar", "beaucoup", "because of", "before", "behind", "below", "beneath", "beside", "besides", "best part of", "between", "beyond", "bofe", "boku", "bolth", "bookoo", "both", "bothe", "buku", "but", "by", "ca", "certain", "cha", "chez", "circa", "close to", "co's", "come", "concerning", "counter to", "couple", "cross", "da", "dat", "de", "dehors", "dem", "dese", "despite", "dis", "down", "down on", "doze", "due to", "during", "e'ry", "each", "each and every", "each other", "ebery", "either", "em", "enny", "enough", "enuf", "enuff", "eny", "euerie", "euery", "ever", "everie", "everwhat", "every", "everybody", "everyone", "everything", "except", "except for", "eyther", "far from", "few", "fewer", "fewest", "fewscore", "fiew", "following", "for", "forward", "from", "fuck all", "gainst", "he", "hecka", "hella", "her", "hers", "herself", "hes", "hevery", "him", "himself", "his", "hits", "hoi", "how many", "how much", "hundredsome", "hys", "idem", "illness)", "in", "including", "inside", "inside of", "instead of", "into", "it", "it's", "its", "itself", "last", "le", "least", "left of", "less", "less and less", "like", "little", "ma", "mah", "mai", "many", "many a", "many another", "manye", "me", "mickle", "mid", "midst", "mine", "minus", "more", "more and more", "mos'", "most", "much", "muchee", "muchell", "muh", "my", "myself", "nantee", "nanti", "nanty", "nary a", "naught", "near", "near to", "nearer", "nearest", "neath", "neither", "next", "next to", "nil", "no", "no one", "nobody", "nobody's", "none", "nope", "not a little", "not even one", "nothing", "notwithstanding", "nought", "nuntee", "nunty", "o'", "o'er", "of", "off", "on", "one", "one and the same", "one another", "one or two", "onto", "opposite", "opposite of", "opposite to", "other", "other than", "others", "ought", "our", "ours", "ourself", "ourselves", "out", "out from", "out of", "outside", "outside of", "over", "overmuch", "owing to", "owne", "pace", "past", "per", "plenty", "plus", "post", "pre", "prior to", "pro", "pursuant to", "q", "quite a few", "quodque", "rather than", "re", "regardless of", "right of", "said", "sans", "sauf", "save", "sech", "several", "severall", "she", "short", "since", "sithence", "som", "some", "some few", "some kind of", "some kinda", "some ol'", "some old", "some ole", "somebody", "someone", "something", "somewhat", "sorra", "spite", "subsequent to", "such", "such as", "such-and-such", "suchlike", "sufficient", "t'", "teh", "than", "thanks to", "that", "that there", "thatt", "thay", "the", "thee", "their", "theirs", "theirself", "theirselves", "them", "themself", "themselves", "there", "these", "thet", "they", "they're", "they's", "thilk", "thine", "thir", "this", "this here", "tho", "those", "thou", "thousandsome", "through", "throughout", "thru", "thy", "Thy", "thyself", "til", "till", "to", "together", "too many", "too much", "toward, towards", "towards", "tree)", "umpteen", "under", "underneath", "unlike", "until", "unto", "up", "up to", "upon", "upside", "us", "various", "versus", "via", "vice", "vich", "vis-à-vis", "vs", "wat", "we", "what", "whate'er", "whatevah", "whatever", "whatevuh", "whath", "whatnot", "whatsoever", "whence", "where", "whereby", "wherefrom", "wherein", "whereinto", "whereof", "whereon", "wheresoever", "whereto", "whereunto", "wherever", "wherewith", "wherewithal", "whether", "which", "whichever", "whichsoever", "who", "whoever", "whom", "whomever", "whomso", "whomsoever", "whose", "whosesoever", "whosever", "whoso", "whosoever", "whoze", "with", "within", "without", "wor", "worth", "xyr", "y'all", "ya", "ye", "yer", "yes", "yisser", "yizzer", "yo", "yo'", "yon", "yonder", "yonders", "you", "your", "yours", "yourself", "yourselves", "yous", "youse", "yousser", "yr", "yup", "yure", "zis", "and", "or", "if", 'best', 'worst', 'really', 'quite',]