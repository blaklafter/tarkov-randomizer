import os
import pprint
import requests

from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

class TarkovMap:
  name = ""
  features = ""
  duration = ""
  players = ""
  enemies = ""
  release_state = ""
  
  def __init__(self, parsed_map_data):
    self.name = parsed_map_data[1]
    self.duration = parsed_map_data[2]
    self.players = parsed_map_data[3]
    self.enemies = parsed_map_data[4]
    self.release_state = parsed_map_data[5]


data_types = {
    'maps':
    {
      'url': 'https://escapefromtarkov.gamepedia.com/Map_of_Tarkov',
      'url_save': 'map.html',
    },
  }

def download_page_HTML(data_type):
  mapPageData = requests.get(data_type)
  return mapPageData.text

def get_page_HTML(data_type, over_write=True):
  save_file = os.path.join('data', data_type['url_save'])
  page_text = None
  if not os.path.exists(save_file) or over_write is True:
    with open(save_file, 'w+') as f:
      print('Downloading and writing to {0}'.format(save_file))
      page_text = download_page_HTML(data_type['url'])
      f.write(page_text)

  if not page_text:
    with open(save_file, 'r') as f:
      print("Reading {0}".format(save_file))
      page_text = f.read()
  
  return page_text

def parse_page_data(data_type):
  page_text = get_page_HTML(data_types['maps'], over_write = False)
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

if __name__ == '__main__':
  parse_page_data(data_types['maps'])