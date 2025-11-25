
import pycountry
import csv
from collections import OrderedDict
from thefuzz import process
import pathlib

## Manual overrides for countries with historic or alternate names
manual_name_map = {
    'BURMA': 'Myanmar',
    'BAHAMAS, THE': 'Bahamas',
    'CAPE VERDE': 'Cabo Verde',
    'CZECH REPUBLIC': 'Czechia',
    'CONGO, DEMOCRATIC REPUBLIC OF THE': 'Congo, The Democratic Republic of the',
    'CONGO, REPUBLIC OF THE': 'Congo',
    'GAMBIA, THE': 'Gambia',
    'IRAN': 'Iran, Islamic Republic of',
    'KOREA, NORTH': 'Korea, Democratic People\'s Republic of',
    'KOREA, SOUTH': 'Korea, Republic of',
    'LAOS': 'Lao People\'s Democratic Republic',
    'MACEDONIA': 'North Macedonia',
    'MOLDOVA': 'Moldova, Republic of',
    'WEST BANK': 'West Bank',
    'GAZA STRIP': 'Gaza Strip',
    'RUSSIA': 'Russian Federation',
    'SYRIA': 'Syrian Arab Republic',
    'TAIWAN': 'Taiwan, Province of China',
    'TANZANIA': 'Tanzania, United Republic of',
    'UNITED STATES': 'United States',
    'VIETNAM': 'Viet Nam',
    # Add more known alias mappings as needed
}

# Extract country names from CSV
filename = pathlib.Path(__file__).parent.parent.parent/'data'/'economy_data.csv'
country_names = []
with open(filename, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        country = row['Country'].strip()
        if country and country not in country_names:
            country_names.append(country)

country_names_pycountry = []
for c in pycountry.countries:
    country_names_pycountry.append(c.name)
    """ if hasattr(c, 'official_name'):
        country_names_pycountry.append(c.official_name)
    if hasattr(c, 'common_name'):
        country_names_pycountry.append(c.common_name) """
country_names_pycountry = list(set(country_names_pycountry))

country_map = OrderedDict()
for name in country_names:
    # Check manual override first
    if name.upper() in manual_name_map:
        country_map[name] = manual_name_map[name.upper()]
        continue
    best_match, score = process.extractOne(name, country_names_pycountry)
    if score >= 80:
        country_map[name] = best_match
    else:
        country_map[name] = None

print(country_map)