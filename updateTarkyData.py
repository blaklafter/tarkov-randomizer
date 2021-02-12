import os
import pprint
import requests

from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

class TarkovWiki:
  data_types = {
      'maps':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Map_of_Tarkov',
        'url_save': 'map.html',
      },
      'weapons':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Weapons',
        'url_save': 'weapon.html',
      },
      'armor':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Armor_vests',
        'url_save': 'armor.html'
      },
      'backpacks':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Backpacks',
        'url_save': 'backpack.html'
      },
      'rigs':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Chest_rigs',
        'url_save': 'rig.html'
      },
      'headwear':
      {
        'url': 'https://escapefromtarkov.gamepedia.com/Headwear',
        'url_save': 'headwear.html'
      },
    }
  
  @staticmethod
  def validate_data_type(data_type):
    if data_type in TarkovWiki.data_types:
      return TarkovWiki.data_types[data_type]
    
    raise Exception('Invalid data_type: {0}'.format(data_type))

  @staticmethod
  def download_page_HTML(url):
    mapPageData = requests.get(url)
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

if __name__ == '__main__':
  over_write = False

  armor = parse_data('armor', over_write)
  maps = parse_data('maps', over_write)
  weapons = parse_data('weapons', over_write)
  backpacks = parse_data('backpacks', over_write)
  rig = parse_data('rigs', over_write)
  headwear = parse_data('headwear', over_write)

  pp.pprint(maps)
  #pp.pprint(armor)
  #pp.pprint(weapons)
  #pp.pprint(backpacks)
  #pp.pprint(rig)
  #pp.pprint(headwear)