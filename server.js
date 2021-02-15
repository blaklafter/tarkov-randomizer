const express = require('express');
const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');

require('dotenv').config();
const url = process.env.MONGO_CONN_STR
const dbName = process.env.DATABASE

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
  return documents
}

const app = express()
const port = 3000

app.use('/', express.static('public'))

app.get('/maps', async (req, res) => {
  docs = await findDocuments(mongodb, 'maps', {'Release State': 'Released'})
  res.send(docs.map( d => d['Name']))
})

app.get('/weapons', async (req, res) => {
  docs = await findDocuments(mongodb, 'weapons', {})
  res.send(docs.map( d => d['Name']))
})

app.get('/armor', async (req, res) => {
  docs = await findDocuments(mongodb, 'armor', {})
  res.send(docs.map( d => d['Name']))
})

app.get('/backpacks', async (req, res) => {
  docs = await findDocuments(mongodb, 'backpacks', {})
  res.send(docs.map( d => d['Name']))
})

app.get('/rigs', async (req, res) => {
  docs = await findDocuments(mongodb, 'rigs', {})
  res.send(docs.map( d => d['Name']))
})

app.get('/headwear', async (req, res) => {
  docs = await findDocuments(mongodb, 'headwear', {})
  res.send(docs.map( d => d['Name']))
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})