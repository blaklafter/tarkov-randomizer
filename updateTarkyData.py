import os
import pprint
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
pp = pprint.PrettyPrinter(indent=4)

class TarkovWiki:
  data_types = {
      'maps':
      {
        'url': 'https://escapefromtarkov.fandom.com/Map_of_Tarkov',
        'url_save': 'map.html',
        'unique_field': 'Name',
      },
      'weapons':
      {
        'url': 'https://escapefromtarkov.fandom.com/Weapons',
        'url_save': 'weapon.html',
        'unique_field': 'Name',
      },
      'armor':
      {
        'url': 'https://escapefromtarkov.fandom.com/Armor_vests',
        'url_save': 'armor.html',
        'unique_field': 'Name',
      },
      'backpacks':
      {
        'url': 'https://escapefromtarkov.fandom.com/Backpacks',
        'url_save': 'backpack.html',
        'unique_field': 'Name',
      },
      'rigs':
      {
        'url': 'https://escapefromtarkov.fandom.com/Chest_rigs',
        'url_save': 'rig.html',
        'unique_field': 'Name',
      },
      'headwear':
      {
        'url': 'https://escapefromtarkov.fandom.com/Headwear',
        'url_save': 'headwear.html',
        'unique_field': 'Name',
      },
    }
  
  @staticmethod
  def validate_data_type(data_type):
    if data_type in TarkovWiki.data_types:
      return TarkovWiki.data_types[data_type]
    
    raise Exception('Invalid data_type: {0}'.format(data_type))

  @staticmethod
  def download_page_HTML(url):
    headers = {
      'User-Agent': 'tarkov-randomizer/0.2 (https://tarkov-randomizer.com; isaacschwarz3@gmail.com) python-requests/2.22 bot'
    }
    mapPageData = requests.get(url, headers)
    return mapPageData.text

  @staticmethod
  def get_page_HTML(data_type, over_write=True):
    data_ctx = TarkovWiki.validate_data_type(data_type)

    save_file = os.path.join('data', data_ctx['url_save'])
    page_text = None
    if not os.path.exists(save_file) or over_write is True:
      with open(save_file, 'w+') as f:
        print('Downloading and writing to {0}'.format(save_file))
        page_text = TarkovWiki.download_page_HTML(data_ctx['url'])
        f.write(page_text)

    if not page_text:
      with open(save_file, 'r') as f:
        print("Reading {0}".format(save_file))
        page_text = f.read()
    
    return page_text
  
def parse_data(data_type, over_write):
  tables = get_data_from_html(data_type, over_write)

  items = []

  for table in tables:

    item_class = trim_text(table.find_previous('h1').get_text()) if table.find_previous('h1') else 'None'
    item_type = trim_text(table.find_previous('h2').get_text()) if table.find_previous('h2') else 'None'
    item_subtype = trim_text(table.find_previous('h3').get_text()) if table.find_previous('h3') else 'None'

    parsed_classifications = (item_class, item_type, item_subtype)

    if is_skippable_table(parsed_classifications):
      continue

    table_rows = table.findAll('tr')

    # First row should be a header, if not, EXPLODE
    if not is_header_row(table_rows[0], 'th', 2):
      pprint.pprint(table_rows[0])
      raise(Exception('This does not seem to be a header row'))

    # Parse out item metadata
    item_metadata = get_data_items(table_rows[0], 'th')

    # Parse out item data
    for table_row in table_rows[1:]:
      item = {}
      # Add item type and subtype
      item['parsed_class'] = item_class
      item['parsed_type'] = item_type
      item['parsed_subtype'] = item_subtype

      item_data = get_data_items(table_row, ['td', 'th'])
      for datum in item_data:
        item[item_metadata[item_data.index(datum)]] = datum

      items.append(item)

  return items

def get_data_from_html(page_type, over_write):
  page_text = TarkovWiki.get_page_HTML(page_type, over_write)
  page = BeautifulSoup(page_text, 'lxml')
  return page.findAll('table', class_="wikitable")

def is_skippable_table(pc):
  return is_skippable_armor_table(pc[1]) or \
    is_skippable_weapon_table(pc[1]) or \
    is_skippable_backpack_table(pc[1]) or \
    is_skippable_rig_table(pc[0])

def is_skippable_armor_table(item_type):
  skippable_types = ['Upcoming Body Armor', ]
  return item_type in skippable_types

def is_skippable_weapon_table(item_type):
  skippable_types = ['Unconfirmed weapons', 'Upcoming weapons', 'Throwable weapons', 'Melee weapons', 'Stationary weapons']
  return item_type in skippable_types

def is_skippable_backpack_table(item_type):
  skippable_types = ['Upcoming backpacks']
  return item_type in skippable_types

def is_skippable_rig_table(item_class):
  skippable_types = ['Upcoming Chest Rigs', ]
  return item_class in skippable_types

def trim_text(input_string):
  trimmed = input_string.strip().replace(u'\xa0', u' ')
  try:
    left_bracket_index = trimmed.index('[')
    if left_bracket_index:
      trimmed = trimmed[:left_bracket_index]
  except:
    pass

  return trimmed

def is_header_row(bs_node, header_element, header_minimum_count):
  return len(bs_node.findAll(header_element)) >= header_minimum_count

def get_data_items(bs_node, nodes):
  metadata_items = []

  weapon_metadata = bs_node.findAll(nodes)
  for metadata in weapon_metadata:
    md = trim_text(metadata.get_text())
    metadata_items.append(md)
  return metadata_items

def get_db(client, database):
  return client[database]

if __name__ == '__main__':

  client = MongoClient(os.getenv('MONGO_CONN_STR'))
  db = get_db(client, os.getenv('DATABASE'))

  # Setting this to False will not get new data from the wiki if data already exists
  over_write = True

  for data_type in TarkovWiki.data_types:
    pp.pprint("Processing: {0}".format(data_type))
    parsed_data = parse_data(data_type, over_write)

    unique_field = TarkovWiki.data_types[data_type]['unique_field']

    db[data_type].create_index(unique_field, unique=True)
    matched = 0
    modified = 0
    upserted = 0
    for m in parsed_data:
      result = db[data_type].replace_one({unique_field: m[unique_field]}, m, upsert=True)
      matched = matched + result.matched_count
      modified = modified + result.modified_count
      upserted = upserted + 1 if result.upserted_id else 0
    print("{0} -- matched: {1}, modified: {2}, upserted: {3}".format(data_type, matched, modified, upserted))