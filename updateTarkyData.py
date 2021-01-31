import os
import requests

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

def save_page_HTML(data_type, over_write=True):
  save_file = os.path.join('data', data_type['url_save'])
  if not os.path.exists(save_file) or over_write is True:
    with open(save_file, 'w+') as f:
      print('Downloading and writing to {0}'.format(save_file))
      f.write(download_page_HTML(data_type['url']))

if __name__ == '__main__':
  save_page_HTML(data_types['maps'], over_write = False)