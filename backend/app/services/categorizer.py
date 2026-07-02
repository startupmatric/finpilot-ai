from typing import Dict

# Simple rule-based categorization
CATEGORY_RULES: Dict[str, str] = {
    'starbucks': 'Food & Dining',
    'swiggy': 'Food & Dining',
    'zomato': 'Food & Dining',
    'whole foods': 'Food & Dining',
    'uber': 'Transport',
    'ola': 'Transport',
    'lyft': 'Transport',
    'netflix': 'Entertainment',
    'prime video': 'Entertainment',
    'spotify': 'Entertainment',
    'amazon': 'Shopping',
    'flipkart': 'Shopping',
    'apple store': 'Shopping',
    'walmart': 'Shopping',
    'target': 'Shopping',
}

def categorize_transaction(merchant: str) -> str:
    """
    Categorize a transaction based on merchant name.
    Returns category or 'Other' if no rule matches.
    """
    merchant_lower = merchant.lower().strip()
    
    # Check for exact or partial matches
    for keyword, category in CATEGORY_RULES.items():
        if keyword in merchant_lower:
            return category
    
    return 'Other'

def get_all_categories() -> list:
    """Return all unique categories"""
    return list(set(CATEGORY_RULES.values())) + ['Other']