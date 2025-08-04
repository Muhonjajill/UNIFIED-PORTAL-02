# priority_rules.py

import re

PRIORITY_MATRIX = {
    'technical outage': {
        'software': 'high',
        'software update': 'low',
        'maintenance': 'medium',
        'preventive maintenance': 'low',
        'hardware error': 'critical',
        'installation and configuration': 'medium',
        'network and connection error': 'high',
        'repair': 'high',
        'security': 'high',
        'complaint': 'medium',
        'other': 'low',
    },
    'cybersecurity incident': {
        'security': 'critical',
        'software': 'high',
        'other': 'high',
    },
    'client complaint': {
        'complaint': 'medium',
        'software': 'low',
        'hardware error': 'high',
        'network and connection error': 'medium',
        'security': 'high',
        'other': 'low',
    },
    'sla breach': {
        'software': 'medium',
        'hardware error': 'high',
        'security': 'high',
        'other': 'medium',
    }
}

# Synonym mapping for flexible matching
SYNONYMS = {
    'failure': {'failure', 'crash', 'fault', 'error', 'malfunction', 'hang'},
    'booting': {'booting', 'starting', 'initializing'},
    'not': {'not', 'no', "can't", 'unable', 'fail', 'fails', 'doesn’t', 'isn’t'},
    'working': {'working', 'functioning', 'responding', 'operational'},
    'printer': {'printer', 'receipt', 'printer'},
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

# Define patterns using word sets (flexible order, token-based match)
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

def determine_priority(issue_type, problem_category, description=''):
    issue_type = issue_type.lower().strip()
    problem_category = problem_category.lower().strip()
    words = set(normalize(description))  # Convert to set for subset matching

    # Synonym-aware pattern matching
    for level, patterns in PRIORITY_PATTERNS.items():
        for pattern in patterns:
            if all(
                any(syn in words for syn in expand_keywords_with_synonyms({token}))
                for token in pattern
            ):
                return level
            
    # Fallback: Use issue_type + problem_category from the matrix
    return PRIORITY_MATRIX.get(issue_type, {}).get(problem_category, 'low')
