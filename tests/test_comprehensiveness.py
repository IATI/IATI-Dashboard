import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import comprehensiveness

mock_stats = {
    'comprehensiveness': {
        'activity-date': 2,
        'activity-status': 2,
        'recipient_language': 0,
        'transaction_spend': 1,
    },
    'comprehensiveness_denominator_default': 2,
    'comprehensiveness_denominators': {
        'recipient_language': 0,
        'transaction_spend': 1,
        'transaction_traceability': 1
    }
}


def test_denominator():
    assert comprehensiveness.denominator('activity-date', mock_stats) == 2
    assert comprehensiveness.denominator('transaction_spend', mock_stats) == 1
    assert comprehensiveness.denominator('non_existant_key', mock_stats) == 2  # Passing a non existant key will return the default denominator
    assert comprehensiveness.denominator('activity-date', None) == 0  # Passing a 'Falsey' value as the stats param will return 0
