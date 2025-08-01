# priority_rules.py

import re

PRIORITY_MATRIX = {
    'technical outage': {
        'software': 'low',
        'software update': 'low',
        'maintenance': 'medium',
        'preventive maintenance': 'low',
        'hardware error': 'high',
        'installation and configuration': 'medium',
        'network and connection error': 'high',
        'repair': 'medium',
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

# Define patterns using word sets (flexible order, token-based match)
PRIORITY_PATTERNS = {
    'critical': [
        
        {'system', 'down'},
        {'data', 'leak'},
        {'total', 'failure'},
        {'unauthorized', 'access'},
        {'terminal', 'offline'},
        {'server', 'offline'},
        {'full', 'outage'},
        {'security', 'incident'},
        {'machine', 'not', 'booting'},
        {'safe', 'lock', 'not', 'opening'},
        {'cash', 'unit', 'error'},

        {'system', 'failure'},
        {'completely', 'down'},
        {'ransomware'},
        {'hacked'},
    ],
    'high': [
        {'network', 'problem'},
        {'data', 'lost'},
        {'data', 'issue'},
        {'multiple', 'users'},
        {'application', 'error'},
        {'not', 'picking', 'notes'},
        {'safe', 'lock', 'error'},
        {'note', 'jam'},
        {'stacked', 'notes'},


        {'frequent', 'disconnection'},
        {'cannot', 'login'},
        {'blocked', 'access'},
        {'installation', 'failed'},
        {'error', 'startup'},
    ],
    'medium': [
        {'slow', 'performance'},
        {'screen', 'flickering'},
        {'configuration', 'issue'},
       
        {'users', 'added'},

        {'usb', 'not', 'detected'},
        {'intermittent', 'issue'},
        {'one', 'terminal'},
    ],
    'low': [
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

def determine_priority(issue_type, problem_category, description=''):
    issue_type = issue_type.lower().strip()
    problem_category = problem_category.lower().strip()
    words = set(normalize(description))  # Convert to set for subset matching

    # First: Try flexible token-based matching
    for level, patterns in PRIORITY_PATTERNS.items():
        for pattern in patterns:
            if pattern.issubset(words):
                return level

    # Fallback: Use issue_type + problem_category from the matrix
    return PRIORITY_MATRIX.get(issue_type, {}).get(problem_category, 'low')
