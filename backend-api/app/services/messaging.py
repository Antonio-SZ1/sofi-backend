import pika
from datetime import datetime
import json
import logging
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_event(event_type: str, entity_id: str, payload: dict):
    """Publica un evento en RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        channel = connection.channel()

        exchange_name = 'sofipo_events_exchange'
        routing_key = f"sofipo.{event_type.replace('_', '.')}" 

        channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

        message = {
            "event_type": event_type,
            "entity_id": str(entity_id),
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  
            ))
        
        logger.info(f"Published event '{event_type}' to RabbitMQ with routing key '{routing_key}'")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to publish event to RabbitMQ: {e}")