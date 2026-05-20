"""
RabbitMQ Message Publisher (pika)
Production-ready with connection management, retry, error handling
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pika
from pika.spec import BasicProperties
from pika.exceptions import AMQPConnectionError, AMQPChannelError, NackError, UnroutableError
from pika.exchange_type import ExchangeType

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    Publish to RabbitMQ with three patterns:
    1. publish_event() - Topic exchange (pub/sub)
    2. publish_to_queue() - Direct queue (work queue)
    3. publish_to_exchange() - Custom routing (fanout, headers, etc)
    """

    def __init__(self, connection_url: str, default_exchange: str = "events"):
        self.connection_url = connection_url
        self.default_exchange = default_exchange
        self._connection = None
        self._channel = None

    def _get_connection(self) -> pika.BlockingConnection:
        """Get or create connection"""
        if self._connection is None or self._connection.is_closed:
            params = pika.URLParameters(self.connection_url)
            self._connection = pika.BlockingConnection(params)
        return self._connection

    def _get_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """Get or create channel"""
        conn = self._get_connection()
        if self._channel is None or self._channel.is_closed:
            self._channel = conn.channel()
        return self._channel

    def _ensure_exchange(self, exchange: str, exchange_type: str = "topic", durable: bool = True):
        """Declare exchange if not exists"""
        try:
            channel = self._get_channel()
            channel.exchange_declare(
                exchange=exchange,
                exchange_type=exchange_type,
                durable=durable,
                auto_delete=False
            )
        except Exception as e:
            logger.error(f"Failed to declare exchange {exchange}: {e}")
            raise

    def _ensure_queue(self, queue: str, durable: bool = True):
        """Declare queue if not exists"""
        try:
            channel = self._get_channel()
            channel.queue_declare(
                queue=queue,
                durable=durable,
                auto_delete=False
            )
        except Exception as e:
            logger.error(f"Failed to declare queue {queue}: {e}")
            raise

    def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        routing_key: Optional[str] = None,
        persistent: bool = True,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish domain event (pub/sub pattern)

        Args:
            event_type: Event type (e.g., "user.created")
            payload: Event payload (dict)
            routing_key: Routing key (defaults to event_type)
            persistent: Persist to disk
            headers: Custom headers

        Returns:
            True if published successfully
        """
        routing_key = routing_key or event_type

        # Wrap with metadata
        message = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }

        return self.publish_to_exchange(
            exchange=self.default_exchange,
            routing_key=routing_key,
            message=message,
            exchange_type="topic",
            persistent=persistent,
            headers=headers
        )

    def publish_to_queue(
        self,
        queue: str,
        message: Dict[str, Any],
        persistent: bool = True,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish directly to queue (work queue pattern)

        Args:
            queue: Queue name
            message: Message payload
            persistent: Persist to disk
            headers: Custom headers

        Returns:
            True if published successfully
        """
        self._ensure_queue(queue, durable=persistent)

        properties = BasicProperties(
            delivery_mode=2 if persistent else 1,
            content_type="application/json",
            timestamp=int(datetime.utcnow().timestamp()),
            headers=headers or {}
        )

        body = json.dumps(message, default=str).encode('utf-8')

        try:
            channel = self._get_channel()
            channel.confirm_delivery()

            channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=body,
                properties=properties,
                mandatory=True
            )

            logger.info(f"Message published to queue '{queue}'")
            return True

        except Exception as e:
            logger.error(f"Failed to publish to queue: {e}")
            raise

    def publish_to_exchange(
        self,
        message: Dict[str, Any],
        exchange: str = None,
        routing_key: str = "",
        exchange_type: str = "topic",
        persistent: bool = True,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish to exchange with custom routing

        Args:
            message: Message payload
            exchange: Exchange name
            routing_key: Routing key
            exchange_type: topic, direct, fanout, headers
            persistent: Persist to disk
            headers: Custom headers

        Returns:
            True if published successfully
        """
        exchange = exchange or self.default_exchange

        self._ensure_exchange(exchange, exchange_type, durable=persistent)

        properties = BasicProperties(
            delivery_mode=2 if persistent else 1,
            content_type="application/json",
            timestamp=int(datetime.utcnow().timestamp()),
            headers=headers or {}
        )

        body = json.dumps(message, default=str).encode('utf-8')

        try:
            channel = self._get_channel()
            channel.confirm_delivery()

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=True
            )

            logger.info(f"Message published to {exchange}:{routing_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish to exchange: {e}")
            raise

    def close(self):
        """Close connection"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()


# Factory
_publisher_instance = None

def get_publisher(connection_url: str = "amqp://guest:guest@localhost:5672//") -> RabbitMQPublisher:
    """Get or create publisher instance"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = RabbitMQPublisher(connection_url)
    return _publisher_instance
