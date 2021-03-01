const items = [
  { 'id': 'weapon', 'url': 'weapons', 'data': null, 'lastUpdate': null },
  { 'id': 'map', 'url': 'maps', 'data': null, 'lastUpdate': null },
  { 'id': 'headwear', 'url': 'headwear', 'data': null, 'lastUpdate': null },
  { 'id': 'backpack', 'url': 'backpacks', 'data': null, 'lastUpdate': null },
  { 'id': 'rig', 'url': 'rigs', 'data': null, 'lastUpdate': null },
  { 'id': 'armor', 'url': 'armor', 'data': null, 'lastUpdate': null }];

const knobs = {
  'map': 0,
  'weapon': 5,
  'headwear': 10,
  'armor': 10,
  'rig': 10,
  'backpack': 10
};

const getAllItems = async (initial) => {
  itemList = [...items]

  while(itemList.length > 0) {
    item = itemList.pop();

    //only add a knob onload and don't add one for the maps cause that would be stupid
    if(initial && item.id !== 'map') {
      zeroKnob(item.id);
    }

    await fetchItemData(item.id);
    getItems(item);
  }
};

const fetchItemData = async (item) => {
  const idx = items.findIndex(i => i.id === item);
  refreshMS = 1000 * 60 * 10; // update if it hasn't been updated in 10 minutes

  if(!items[idx].data || Date.now() - refreshMS >= items[idx].lastUpdate) {
    const url = items[idx].url;

    const data = await fetch(url);
    const res = await data.text();
    items[idx].data = JSON.parse(res);
    items[idx].lastUpdate = Date.now();
    return;
  }
};

const getItems = (item) => {
  if (typeof(item) === 'string'){
    item = items.find(i => i.id === item);
    if(!item) {
      console.error(`Invalid data supplied: ${item}`);
      return;
    }
  }

  const itemElement = (specifiedItem) => document.getElementById(specifiedItem || item.id).querySelectorAll('div.item-name')[0];
  
  // text change animation
  itemElement().classList.add('add-text');
  setTimeout(() => {itemElement().classList.remove('add-text');}, 1000);

  // map cannot be None
  if( item.id !== 'map') {
    selectedChanceForNone = knobs[item.id]

    chanceForNone = selectedChanceForNone || 0;

    // is None is "rolled" then we don't need to get a random item
    if(Math.random() * 100 <= chanceForNone) {
      updateElement(item, "None");
      return;
    }
  }
  
  updateElement(item, item.data);
  fetchItemData(item.id);
};

const updateElement = (item, data) => {
  const itemElement = (specifiedItem) => document.getElementById(specifiedItem || item.id).getElementsByClassName('item-name')[0];
  
  if(data === 'None') {
    itemElement().textContent = data;
    if(item.id === 'rig') {
      itemElement('armor').classList.remove('conflicting-item');
    }
    return;
  }

  selectedItem = chooseRandom(data);

  // check for armored rig, if it is, mark the armor as conflicting
  if(item.id === 'rig'){
    if(selectedItem['type'] == 'Armored'){
      itemElement('armor').classList.add('conflicting-item');
    } else {
      itemElement('armor').classList.remove('conflicting-item');
    }
    delayedUpdate(itemElement(), selectedItem['name'], 250)
    return;
  }

  delayedUpdate(itemElement(), selectedItem, 250)
};

const delayedUpdate = (element, elementText, msDelay) => {
  setTimeout(() => {element.textContent = elementText}, msDelay);
};

const chooseRandom = (items) => {
  const item = items[Math.floor(Math.random() * items.length)];
  return item
};

function zeroKnob(elementId) {
  const defaultKnobValue = knobs[elementId];
  // Create knob element, 70 x 70 px in size.
  const knob = pureknob.createKnob(70, 70);

  // Set properties.
  knob.setProperty('angleStart', -0.75 * Math.PI);
  knob.setProperty('angleEnd', 0.75 * Math.PI);
  knob.setProperty('colorFG', '#88ff88');
  knob.setProperty('trackWidth', 0.4);
  knob.setProperty('valMin', 0);
  knob.setProperty('valMax', 100);

  // Set initial value.
  knob.setValue(defaultKnobValue || 0);

  /*
   * Event listener.
   *
   * Parameter 'knob' is the knob object which was
   * actuated. Allows you to associate data with
   * it to discern which of your knobs was actuated.
   *
   * Parameter 'value' is the value which was set
   * by the user.
   */
  const listener = function(knob, value) {
    knobs[elementId] = value;
  };

  knob.addListener(listener);

  // Create element node.
  const node = knob.node();

  // Add it to the DOM.
  const elem = document.getElementById(elementId).querySelector('div.none-selector');
  elem.appendChild(node);
}

