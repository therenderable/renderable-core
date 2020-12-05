import json

import pika


class Queue:
  def __init__(self, hostname, port, username, password, heartbeat = 120):
    self.hostname = hostname
    self.port = port
    self.username = username
    self.password = password
    self.heartbeat = heartbeat

    credentials = pika.PlainCredentials(self.username, self.password)

    self.parameters = pika.ConnectionParameters(
      self.hostname, self.port, '/', credentials, heartbeat = self.heartbeat)

  def _wrap_callback(self, callback, model):
    def on_message_callback(channel, method, properties, body):
      message = model(**json.loads(body.decode()))
      callback(channel, method, message)

    return on_message_callback

  def publish(self, message, routing_key):
    raise NotImplementedError

  def consume(self, callback, routing_key, model):
    raise NotImplementedError


class WorkQueue(Queue):
  def publish(self, messages, routing_key):
    routing_key = str(routing_key)

    connection = pika.BlockingConnection(self.parameters)
    channel = connection.channel()

    channel.queue_declare(queue = routing_key, durable = True)

    for message in messages:
      channel.basic_publish(
        exchange = '',
        routing_key = routing_key,
        body = message.json(),
        properties = pika.BasicProperties(delivery_mode = 2))

    connection.close()

  def consume(self, callback, routing_key, model):
    routing_key = str(routing_key)

    connection = pika.BlockingConnection(self.parameters)
    channel = connection.channel()

    channel.queue_declare(queue = routing_key, durable = True)
    channel.basic_qos(prefetch_count = 1)

    channel.basic_consume(queue = routing_key, on_message_callback = self._wrap_callback(callback, model))
    channel.start_consuming()


class EventQueue(Queue):
  def publish(self, message, routing_key):
    routing_key = str(routing_key)

    connection = pika.BlockingConnection(self.parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange = 'event', exchange_type = 'direct')

    channel.basic_publish(
      exchange = 'event',
      routing_key = routing_key,
      body = message.json())

    connection.close()

  def consume(self, callback, routing_key, model):
    routing_key = str(routing_key)

    connection = pika.BlockingConnection(self.parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange = 'event', exchange_type = 'direct')

    result = channel.queue_declare(queue = '', exclusive = True)
    queue_name = result.method.queue

    channel.queue_bind(exchange = 'event', queue = queue_name, routing_key = routing_key)

    channel.basic_consume(
      queue = queue_name,
      on_message_callback = self._wrap_callback(callback, model),
      auto_ack = True)

    channel.start_consuming()
