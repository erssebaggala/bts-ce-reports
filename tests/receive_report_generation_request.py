#!/usr/bin/env python
import pika
import json
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
import subprocess
import logging
import csv
import logging

# Report directory
REPORT_DIR='.'

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

credentials = pika.PlainCredentials(mq_user, mq_pass)
parameters = pika.ConnectionParameters(mq_host,virtual_host=mq_vhost, credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='reports', durable=True)


def generate_report(report_id):
    """Generate report with the provided id """
	
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(db_user, db_pass, db_host, db_name))
    metadata = MetaData()
    
    ReportTaskLog = Table('reports_task_log', metadata, autoload=True, autoload_with=engine, schema="reports")
    Report = Table('reports', metadata, autoload=True, autoload_with=engine, schema="reports")
    ReportCategory = Table('report_categories', metadata, autoload=True, autoload_with=engine, schema="reports")

    Session = sessionmaker(bind=engine)
    session = Session()

    Session = sessionmaker(bind=engine)
    session = Session()

    # Log request in report task log

    report = session.query(Report).filter_by(pk=report_id).first()
    if report is None:
        logging.info("report_id: {} does not exit!".format(report_id))
        return

    category = session.query(ReportCategory).filter_by(pk=report.category_pk).first()

    sanitized_filename = "{}__{}".format(category.name.lower().replace(" ", "_"), report.name.lower().replace(" ", "_"))
    filename = "{}.csv".format(sanitized_filename)
    path_to_file = '{}/{}'.format(REPORT_DIR, filename)

    # Note: Python 2 uses 'wb'
    outfile = open( path_to_file, 'w', newline='')
    outcsv = csv.writer(outfile)

    table_columns = engine.execute(report.query).keys()

    # Write header as the first row
    outcsv.writerow(table_columns)

    result = engine.execute(report.query)
    records = result.fetchall()

    [outcsv.writerow([getattr(curr, column) for column in table_columns]) for curr in records]

    outfile.close()

    return filename


def callback(ch, method, properties, body):
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(db_user, db_pass, db_host, db_name))
    logger.info("Received %r" % body)

    data = json.loads(body.decode())
    task_id = data['task_id']
    try:
        engine.execute(text("UPDATE reports.reports_task_log SET status = :status WHERE pk = :task_id"),status='RUNNING', task_id=task_id)
        logger.info("Task {} marked as RUNNING".format(task_id))
        
        filename = generate_report(data['report_id'])
        
        engine.execute(text("UPDATE reports.reports_task_log SET status = :status, log = :filename WHERE pk = :task_id"), status='FINISHED', filename=filename, task_id=task_id)
        logger.info("Task {} marked as FINISHED".format(task_id))
		
    except Exception as e:
        t= text("UPDATE reports.reports_task_log SET status = :status, log=:log WHERE pk = :task_id")
        engine.execute(t, status='FAILED', log=str(e), task_id=task_id)
        logger.info("Task {} marked as FAILED because of error:{}".format(task_id, str(e)))


channel.basic_consume(on_message_callback=callback,
                      queue='reports',
                      auto_ack=False)

logger.info('Waiting for report generation requests. To exit press CTRL+C')

channel.start_consuming()
