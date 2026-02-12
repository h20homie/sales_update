
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join('data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUTS_DIR = os.path.join(DATA_DIR, 'outputs')
DOCS_DIR = os.path.join('docs')
RECAPS_DIR = os.path.join(DOCS_DIR, 'weekly_recaps')

MARKETS = ['Dallas', 'Austin', 'San Antonio', 'Houston']
ACCOUNTS = ['Tom Thumb', 'Kroger', 'Central Market', 'Whole Foods', 'Market Street']
BRANDS = ['Estate Ridge Cabernet', 'Lone Star Vodka', 'Hill Country IPA', 'Gulf Tequila', 'Prairie Pinot Grigio']
REPS = ['Alex Carter', 'Jordan Lee', 'Taylor Morgan', 'Sam Nguyen', 'Riley Brooks', 'Casey Diaz', 'Jamie Patel', 'Drew Kim']
CATEGORIES = ['Wine', 'Spirits', 'Beer']

def ensure_dirs():
    for d in [DATA_DIR, RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR, DOCS_DIR, RECAPS_DIR]:
        os.makedirs(d, exist_ok=True)
