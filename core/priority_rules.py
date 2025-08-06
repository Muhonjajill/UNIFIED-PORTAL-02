import re

# Fallback priority per problem category
PRIORITY_MATRIX = {
    'software': 'high',
    'software update': 'low',
    'maintenance': 'medium',
    'preventive maintenance': 'low',
    'hardware error': 'critical',
    'installation and configuration': 'medium',
    'network and connection error': 'high',
    'repair': 'high',
    'security': 'critical',
    'complaint': 'medium',
    'sla breach': 'high',
    'other': 'low',
}

# Synonym mapping
SYNONYMS = {
    'failure': {'failure', 'crash', 'fault', 'error', 'malfunction', 'hang'},
    'booting': {'booting', 'starting', 'initializing'},
    'not': {'not', 'no', "can't", 'unable', 'fail', 'fails', 'doesn’t', 'isn’t'},
    'working': {'working', 'functioning', 'responding', 'operational'},
    'printer': {'printer', 'receipt'},
    'jam': {'jam', 'stuck', 'clogged'},
    'unit': {'unit', 'module', 'cassette'},
    'nv': {'nv', 'note', 'validator'},
    'scanner': {'scanner', 'reader'},
    'slot': {'slot', 'tray'},
    'outage': {'outage', 'disruption', 'blackout'},
    'issue': {'issue', 'problem', 'challenge'},
    'safe': {'safe', 'vault'},
    'lock': {'lock', 'door'},
    'cash': {'cash', 'money'},
    'screen': {'screen', 'display'},
    'slow': {'slow', 'laggy', 'sluggish'},
    'login': {'login', 'sign in', 'log in'},
    'router': {'router', 'modem', 'network'},
    'configuration': {'configuration', 'setup', 'settings'},
    'connect': {'connect', 'connection', 'link'},
}

# Patterns grouped by priority
PRIORITY_PATTERNS = {
    'critical': [
        {'note', 'validator', 'printer', 'not', 'coming'},
        {'faulty', 'cassette', 'slot'},
        {'tes', 'sensor', 'failure'},
        {'machine', 'not', 'booting'},
        {'safe', 'lock', 'not', 'opening'},
        {'cash', 'unit', 'error'},
        {'system', 'failure'},
        {'completely', 'down'},
        {'ransomware'},
        {'hacked'},
    ],
    'high': [
        {'unable', 'process', 'request'},
        {'uncleared', 'cassette'},
        {'failed', 'transaction'},
        {'escrow', 'error'},
        {'frequent', 'notification', 'jam'},
        {'cash', 'unit', 'failure'},
        {'terminal', 'not', 'back', 'service'},
        {'out', 'of', 'service'},
        {'terminal', 'error'},
        {'ksk', 'script', 'not', 'uploading'},
        {'cdm', 'displays', 'error'},
        {'ksk', 'failed', 'execute'},
        {'nv', 'control', 'faulty'},
        {'nv', 'scanner', 'faulty'},
        {'note', 'validator', 'faulty'},
        {'sensor', 'error'},
        {'frequent', 'break', 'down'},
        {'cash', 'bag', 'faulty'},
        {'thick', 'value', 'calibration'},
        {'thickness', 'k', 'value', 'faulty'},
        {'machine', 'out', 'service', 'clearing'},
        {'router', 'connection', 'not', 'working'},
        {'customer', 'uncredited', 'amount'},
        {'internal', 'correction', 'error'},
        {'network', 'problem'},
        {'data', 'lost'},
        {'multiple', 'users'},
        {'application', 'error'},
        {'note', 'jam'},
        {'stacked', 'notes'},
        {'cannot', 'login'},
        {'blocked', 'access'},
        {'installation', 'failed'},
        {'error', 'startup'},
        {'not', 'picking', 'notes'},
        {'safe', 'lock', 'error'},
    ],
    'medium': [
        {'user', 'login'},
        {'maintenance'},
        {'printer', 'faulty'},
        {'faulty', 'printer'},
        {'configuration', 'terminal'},
        {'terminal', 'configuration'},
        {'set', 'up'},
        {'excess', 'cash'},
        {'back', 'screen', 'not', 'responding'},
        {'recon'},
        {'logs'},
        {'kich', 'fatal', 'error'},
        {'cim', 'status', 'unknown'},
        {'admin', 'screen', 'loading'},
        {'note', 'jam'},
        {'connection', 'host', 'not', 'functioning'},
        {'connection', 'host', 'problem'},
        {'rollers', 'worn'},
        {'safedoor', 'password', 'forgotten'},
        {'safe', 'combination', 'not', 'working'},
        {'invalid', 'oauth2'},
        {'invalid', 'token'},
        {'auth', '2.0', 'rectification'},
        {'slow', 'performance'},
        {'screen', 'flickering'},
        {'configuration', 'issue'},
        {'users', 'added'},
        {'usb', 'not', 'detected'},
        {'intermittent', 'issue'},
        {'one', 'terminal'},
    ],
    'low': [
        {'expired', 'license'},
        {'ej', 'journal', 'not', 'uploading'},
        {'minor', 'issue'},
        {'cosmetic', 'error'},
        {'just', 'reporting'},
        {'typo'},
        {'feedback'},
        {'suggestion'},
        {'icon', 'missing'},
        {'problem', 'icon'},
        {'issue', 'icon'},
        {'icon'},
    ]
}


def normalize(text):
    """Lowercase and remove punctuation, return word tokens."""
    return re.sub(r'[^\w\s]', ' ', text.lower()).split()


def expand_keywords_with_synonyms(word_set):
    """Expand each word in the pattern with its synonyms."""
    expanded = set()
    for word in word_set:
        expanded |= SYNONYMS.get(word, {word})
    return expanded


def determine_priority(problem_category, description=''):
    problem_category = problem_category.lower().strip()
    words = set(normalize(description))

    scores = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    for level, patterns in PRIORITY_PATTERNS.items():
        for pattern in patterns:
            match_score = sum(
                1 for token in pattern
                if any(syn in words for syn in expand_keywords_with_synonyms({token}))
            )
            # Score increases for partial matches
            scores[level] += match_score

            # Full pattern match takes precedence
            if match_score >= len(pattern):
                # Optional: add logging
                # print(f"[Matched full pattern for {level}]: {pattern}")
                return level

    # Use the level with the highest score
    best_priority = max(scores, key=scores.get)
    if scores[best_priority] > 0:
        return best_priority

    # Fallback to category default
    return PRIORITY_MATRIX.get(problem_category, 'low')
