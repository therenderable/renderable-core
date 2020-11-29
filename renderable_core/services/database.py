import pymongo

from ..models import ContainerDocument, DeviceDocument, JobDocument, TaskDocument


class Database:
  def __init__(self, hostname, port, username, password):
    self.hostname = hostname
    self.port = port
    self.username = username
    self.password = password

    self.client = pymongo.MongoClient(
      self.hostname, int(self.port),
      username = self.username, password = self.password,
      tz_aware = True)

    self.db = self.client['db']

    self.models = {
      'containers': ContainerDocument,
      'devices': DeviceDocument,
      'jobs': JobDocument,
      'tasks': TaskDocument
    }

  def count(self, document_query, collection_name):
    collection = self.db[collection_name]

    return collection.find(document_query).count()

  def find(self, document_query, collection_name):
    collection = self.db[collection_name]
    document = collection.find_one(document_query)

    return document if document is None else self.models[collection_name](**document)

  def find_many(self, document_query, collection_name):
    collection = self.db[collection_name]
    documents = collection.find(document_query)

    return [self.models[collection_name](**document) for document in documents]

  def save(self, document, collection_name):
    collection = self.db[collection_name]
    collection.insert_one(document.dict(by_alias = True))

    return document

  def save_many(self, documents, collection_name):
    collection = self.db[collection_name]
    collection.insert_many([document.dict(by_alias = True) for document in documents])

    return documents

  def update(self, document_query, document, collection_name):
    collection = self.db[collection_name]
    collection.update_one(document_query, {'$set': document.dict(by_alias = True)})

    return document
