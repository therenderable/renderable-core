from bson.objectid import ObjectId


class ObjectID(ObjectId):
  @classmethod
  def __get_validators__(cls):
    yield cls.validate

  @classmethod
  def __modify_schema__(cls, field_schema):
    field_schema.update(type = 'string')

  @classmethod
  def validate(cls, value):
    if not ObjectId.is_valid(value):
      raise ValueError('invalid ID')

    return ObjectID(value)
