#!/usr/bin/env python
import pika
import json
import sqlalchemy as sa

credentials = pika.PlainCredentials('btsuser', 'Password@7')
parameters = pika.ConnectionParameters('192.168.99.100',virtual_host='/bs', credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='reports', durable=True)

data=json.dumps({'report_id': 1})
channel.basic_publish(exchange='',
                      routing_key='reports',
                      body=data)

print(" [x] Sent 'Hello World!'")