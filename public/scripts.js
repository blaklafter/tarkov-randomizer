const getAllItems = () => {
  const items = [
    { 'id': 'weapon', 'url': 'weapons'},
    { 'id': 'map', 'url': 'maps' },
    { 'id': 'headwear', 'url': 'headwear' },
    { 'id': 'armor', 'url': 'armor'},
    { 'id': 'rig', 'url': 'rigs'},
    { 'id': 'backpack', 'url': 'backpacks'}
  ]

  items.forEach(item => {
    getItems(item);
  });
};

const getItems = (item) => {
  const url = item.url;
  fetch(url)
  .then(data => updateElement(item, data))
};

const updateElement = (item, data) => {
  data.text()
  .then(res => {
    const itemElement = document.getElementById(item.id).getElementsByClassName('item-name')[0];
    itemElement.textContent=chooseRandom(JSON.parse(res))
  })
};

const chooseRandom = (items) => {
  return item = items[Math.floor(Math.random() * items.length)];
  
};

