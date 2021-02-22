const items = [
  { 'id': 'weapon', 'url': 'weapons'},
  { 'id': 'map', 'url': 'maps' },
  { 'id': 'headwear', 'url': 'headwear' },
  { 'id': 'backpack', 'url': 'backpacks'},
  { 'id': 'rig', 'url': 'rigs'},
  { 'id': 'armor', 'url': 'armor'}];

const knobs = {
  'map': 0,
  'weapon': 5,
  'headwear': 10,
  'armor': 10,
  'rig': 10,
  'backpack': 10
};

const getAllItems = (initial) => {
  itemList = [...items]

  while(itemList.length > 0) {
    item = itemList.pop();
    //only add a knob onload and don't add one for the maps cause that would be stupid
    if(initial && item.id !== 'map') {
      zeroKnob(item.id);
    }
    getItems(item);
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
  itemElement().classList.add('add-text');

  setTimeout(() => {itemElement().classList.remove('add-text');}, 1000);

  // map cannot be None
  if( item.id !== 'map') {
    selectedChanceForNone = knobs[item.id]

    chanceForNone = selectedChanceForNone || 0;

    if(Math.random() * 100 <= chanceForNone) {
      updateElement(item, "None");
      return;
    }
  }
  
  const url = item.url;
  fetch(url)
  .then(data => updateElement(item, data))
};

const updateElement = (item, data) => {
  const itemElement = (specifiedItem) => document.getElementById(specifiedItem || item.id).getElementsByClassName('item-name')[0];
  
  if(data === 'None') {
    itemElement().textContent = data;
    return;
  }

  data.text()
  .then(res => {
    selectedItem = chooseRandom(JSON.parse(res));

    // check for armored rig, if it is, make armor "None"
    if(item.id === 'rig'){
      if(selectedItem['type'] == 'Armored'){
        //itemElement('armor').textContent = 'None';
        delayedUpdate(itemElement('armor'), 'None', 250)
      }
      //itemElement().textContent = selectedItem['name'];
      delayedUpdate(itemElement(), selectedItem['name'], 250)
      return;
    }

    //itemElement().textContent = selectedItem;
    delayedUpdate(itemElement(), selectedItem, 250)
  })
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

