const child_process = require('child_process');
const express = require('express');
const pino = require('pino')("./logs/tarkov-randomizer.log");
const expressPino = require('express-pino-logger')({
  logger: pino});

logger = expressPino.logger;

const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');

require('dotenv').config();
const url = process.env.MONGO_CONN_STR;
const dbName = process.env.DATABASE;

// This is a global variable we'll use for handing the MongoDB client
var mongodb;

// Create the db connection
MongoClient.connect(url, {poolSize:2, useUnifiedTopology: true}, dbName, function(err, client) {  
  assert.strictEqual(null, err);
  mongodb=client.db(dbName);
});

const findDocuments = async (c, col, filter) => {
  // Get the documents collection
  const collection = c.collection(col);
  // Find some documents
  const documents = await collection.find(filter).toArray();
  return documents;
};

const app = express();
const port = 3000;

app.use(expressPino);
app.use('/', (req, res, next) => {
  next();
}, express.static('public'));

app.get('/maps', async (req, res) => {
  docs = await findDocuments(mongodb, 'maps', {'Release State': 'Released', 'Name': {'$ne': 'Hideout'}});
  res.send(docs.map( d => d['Name']));
});

app.get('/weapons', async (req, res) => {
  docs = await findDocuments(mongodb, 'weapons', {});
  res.send(docs.map( d => d['Name']));
});

app.get('/armor', async (req, res) => {
  docs = await findDocuments(mongodb, 'armor', {});
  res.send(docs.map( d => d['Name']));
});

app.get('/backpacks', async (req, res) => {
  docs = await findDocuments(mongodb, 'backpacks', {});
  res.send(docs.map( d => d['Name']));
});

app.get('/rigs', async (req, res) => {
  docs = await findDocuments(mongodb, 'rigs', {});
  res.send(docs.map( d => {
    return {'name': d['Name'], 'type': d['parsed_type']};
  }));
});

app.get('/headwear', async (req, res) => {
  docs = await findDocuments(mongodb, 'headwear', {});
  res.send(docs.map( d => d['Name']));
});

app.listen(port, () => {
  logger.info(`tarkov-randomizer listening at http://localhost:${port}`);
});

const privateApp = express();
const privatePort = 3001;
privateApp.use(expressPino);

privateApp.use('/', (req, res, next) => {
  next();
}, express.static('private'));

privateApp.get('/updateData', (req, res) => {
  updateData();
  res.send('OK');
});

privateApp.listen(privatePort, 'localhost', () => {
  logger.info(`tarkov-randomizer private api listening at http://localhost:${privatePort}`);
})

const updateData = () => {
  child_process.exec('bin/python updateTarkyData.py', (err, stdout, stderr) => {
    if (err) {
      console.log(err)
      logger.error(err);
      return;
    }
    console.log(stdout)
    logger.debug(stdout);
  });
}