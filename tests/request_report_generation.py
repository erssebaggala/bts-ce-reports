#!/usr/bin/env python
import pika
import json
import sqlalchemy as sa
import os
from sqlalchemy.orm import sessionmaker
import logging

# Report directory
REPORT_DIR='/reports'

logger = logging.getLogger('generate_report_worker')

# logging.basicConfig()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Starting generate report worker...")

mq_user=os.getenv("BTS_MQ_USER", "btsuser")
mq_pass=os.getenv("BTS_MQ_PASS", "Password@7")
mq_host=os.getenv("BTS_MQ_HOST", "192.168.99.100")
mq_vhost=os.getenv("BTS_MQ_VHOST", "/bs")

db_user=os.getenv("BTS_DB_USER", "bodastage")
db_pass=os.getenv("BTS_DB_PASS", "password")
db_host=os.getenv("BTS_DB_HOST", "192.168.99.100")
db_port=os.getenv("BTS_DB_PORT", "5432")
db_name=os.getenv("BTS_DB_NAME", "bts")


engine = sa.create_engine('postgresql://{}:{}@{}/{}'.format(db_user, db_pass, db_host, db_name))
metadata = sa.MetaData()

Session = sessionmaker(bind=engine)
session = Session()

report_task_log = sa.Table(
    'reports_task_log',
    sa.MetaData(),
    sa.Column('pk', sa.Integer, sa.Sequence('seq_reports_task_log_pk', schema='reports'), primary_key=True, nullable=False),
    sa.Column('action', sa.String(200), nullable=False),  # reports.generate
    sa.Column('log', sa.Text),
    sa.Column('options', sa.dialects.postgresql.JSON),
    sa.Column('status', sa.String(200)),  # FAILED,RUNNING,PENDING,STARTED
    sa.Column('modified_by', sa.Integer),
    sa.Column('added_by', sa.Integer),
    sa.Column('date_added', sa.TIMESTAMP, default=sa.func.now(), onupdate=sa.func.now()),
    sa.Column('date_modified', sa.TIMESTAMP, default=sa.func.now()),
    schema=u'reports'
)



credentials = pika.PlainCredentials(mq_user, mq_pass)
parameters = pika.ConnectionParameters(mq_host,virtual_host=mq_vhost, credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='reports', durable=True)

action = 'reports.generate'
status = 'PENDING'
options = {'query':"""SELECT * FROM managedobjects t""", 'filename': 'managedojects', 'format':'csv'}

stmt = report_task_log.insert().returning(report_task_log.c.pk).values(action=action, status=status, options=options)

result = engine.execute(stmt,)

row = result.fetchone()

task_id = row[0]

data=json.dumps({'task_id': task_id})

print(data)
channel.basic_publish(exchange='',
                      routing_key='reports',
                      body=data)


print(" [x] Sent 'Hello World!'")