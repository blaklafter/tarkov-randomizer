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
      }
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

class TarkovMap:
  def __init__(self, parsed_map_data):
    self.maps = []
    self.name = parsed_map_data[1]
    self.duration = parsed_map_data[2]
    self.players = parsed_map_data[3]
    self.enemies = parsed_map_data[4]
    self.release_state = parsed_map_data[5]
  
def parse_map_data():
  page_text = TarkovWiki.get_page_HTML('maps', over_write = False)
  page = BeautifulSoup(page_text, 'lxml')
  table_row = page.find('table', class_="wikitable").findAll('tr')

  map_data = []
  maps = []

  for row in table_row:
    map_data.append([r.get_text().strip() for r in row.findAll('th')])

  for m in map_data:
    if m[0] == 'Banner':
      continue

    maps.append(TarkovMap(m))

  # List of Released Maps
  pp.pprint([mp.name for mp in maps if mp.release_state == 'Released'])

def parse_weapon_data():
  page_text = TarkovWiki.get_page_HTML('weapons', over_write = False)
  page = BeautifulSoup(page_text, 'lxml')

  tables = page.findAll('table', class_="wikitable")
  weapons = {}
  
  for table in tables:
    weapon_type = trim_text(table.find_previous('h2').get_text())
    weapon_subtype = trim_text(table.find_previous('h3').get_text())
    
    weapon_category = "{0}-{1}".format(weapon_type, weapon_subtype).replace(' ', '_')

    weapons[weapon_category] = []

    # Collect the weapons of each type
    weapon_rows = table.findAll('tr')

    # First row should be a header, if not, EXPLODE
    if not is_header_row(weapon_rows[0], 'th', 2):
      pprint.pprint(weapon_rows[0])
      raise(Exception('This does not seem to be a header row'))
    
    weapon_metadata = get_data_items(weapon_rows[0], 'th')

    # Now everythng else should be data about the weapons and it should follow the metadata
    for weapon_row in weapon_rows[1:]:
      weapon = {}
      weapon_data = get_data_items(weapon_row, ['td', 'th'])
      for datum in weapon_data:
        weapon[weapon_metadata[weapon_data.index(datum)]] = datum

      weapons[weapon_category].append(weapon)

    # break after the first table
    #break

  weapon_categories_to_select = [   
    'Primary_weapons-Assault_rifles',
    'Primary_weapons-Assault_carbines',
    'Primary_weapons-Light_machine_guns',
    'Primary_weapons-Submachine_guns',
    'Primary_weapons-Shotguns',
    'Primary_weapons-Designated_marksman_rifles',
    'Primary_weapons-Sniper_rifles',
    'Primary_weapons-Grenade_launchers',
    'Secondary_weapons-Pistols',
  ]

  #pp.pprint([weapon_type for weapon_type in weapons.keys() if weapon_type in weapon_categories_to_select]) #all weapon types
  pp.pprint({ weapon_type: [ weapon['Name'] for weapon in weapons[weapon_type]] for weapon_type in weapons if weapon_type in weapon_categories_to_select})

def parse_ammo_data():
  pass

def parse_armor_data():
  page_text = TarkovWiki.get_page_HTML('armor', over_write = False)
  page = BeautifulSoup(page_text, 'lxml')

  tables = page.findAll('table', class_="wikitable")
  armors = []

  for table in tables: 
    # Skip upcoming body armor table
    if table.find_previous('h2') and trim_text(table.find_previous('h2').get_text()) == 'Upcoming Body Armor':
        continue

    # Collect the armors of each type
    armor_rows = table.findAll('tr')

    # First row should be a header, if not, EXPLODE
    if not is_header_row(armor_rows[0], 'th', 2):
      pprint.pprint(armor_rows[0])
      raise(Exception('This does not seem to be a header row'))

    armor_metadata = get_data_items(armor_rows[0], 'th')

    # Now everythng else should be data about the armors and it should follow the metadata
    for armor_row in armor_rows[1:]:
      armor = {}
      armor_data = get_data_items(armor_row, ['td', 'th'])
      for datum in armor_data:
        armor[armor_metadata[armor_data.index(datum)]] = datum

      armors.append(armor)

    # break after the first table
    #break

  pp.pprint(armors)


def parse_rig_data():
  pass

def parse_backpack_data():
  pass

def parse_helmet_data():
  pass

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
  #parse_map_data() #done
  #parse_weapon_data() #done
  #parse_ammo_data()
  parse_armor_data()
  #parse_rig_data()
  #parse_backpack_data()
  #parse_helmet_data()