import pika
import json
import os
import time
import logging
import couchdb
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
COUCHDB_USER = os.getenv("COUCHDB_USER")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD")
COUCHDB_HOST = os.getenv("COUCHDB_HOST", "couchdb")
COUCHDB_URL = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}:5984/"
COUCHDB_DATABASE = "business_events"

# --- Conexión a CouchDB ---
def connect_couchdb():
    for i in range(10):
        try:
            server = couchdb.Server(COUCHDB_URL)
    
            if COUCHDB_DATABASE in server:
                db = server[COUCHDB_DATABASE]
            else:
                db = server.create(COUCHDB_DATABASE)
            logging.info("Successfully connected to CouchDB.")
            return db
        except Exception as e:
            logging.warning(f"CouchDB connection attempt {i+1}/10 failed: {e}")
            time.sleep(5)
    logging.error("Could not connect to CouchDB after several retries.")
    return None

db = connect_couchdb()

# --- Lógica de RabbitMQ ---
def callback(ch, method, properties, body):
    """Función que se ejecuta al recibir un mensaje."""
    try:
        message = json.loads(body)
        logging.info(f"Received event: {message.get('event_type')}")

        if db:
            doc_id, doc_rev = db.save(message)
            logging.info(f"Event stored in CouchDB with id: {doc_id}")
        else:
            logging.error("Cannot store event, no connection to CouchDB.")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Inicia el consumidor de RabbitMQ."""
    connection = None
    for i in range(10): 
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            logging.info("Successfully connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            logging.warning(f"RabbitMQ connection attempt {i+1}/10 failed. Retrying in 5 seconds...")
            time.sleep(5)

    if not connection:
        logging.error("Could not connect to RabbitMQ. Exiting.")
        return

    channel = connection.channel()
    exchange_name = 'sofipo_events_exchange'
    queue_name = 'couchdb_event_log_queue'
    
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    
    channel.queue_declare(queue=queue_name, durable=True)
    
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='sofipo.#')
    
    channel.basic_qos(prefetch_count=1) 
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
    logging.info('Waiting for events. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    start_consumer()