"""
Redis Pub/Sub Publisher (redis-py)
Real-time messaging, lightweight, fast
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import redis

logger = logging.getLogger(__name__)


class RedisPublisher:
    """
    Publish to Redis Pub/Sub channels
    Use for real-time, high-frequency updates
    """

    def __init__(self, redis_client: redis.Redis = None, host: str = "localhost", port: int = 6379):
        """
        Initialize Redis publisher

        Args:
            redis_client: Redis client (or create from host/port)
            host: Redis host
            port: Redis port
        """
        self.redis = redis_client or redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30
        )

    def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """
        Publish message to channel

        Args:
            channel: Channel name
            message: Message dict

        Returns:
            Number of subscribers that received message
        """
        try:
            body = json.dumps(message, default=str)
            count = self.redis.publish(channel, body)
            logger.info(f"Published to {channel}, {count} subscribers received")
            return count
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            raise

    def publish_to_pattern(self, pattern: str, message: Dict[str, Any]) -> int:
        """
        Publish to pattern-matched channels (e.g., user:*:notifications)

        Note: Redis doesn't support pattern publishing directly,
        so this publishes to the pattern string itself.

        Args:
            pattern: Channel pattern
            message: Message dict

        Returns:
            Number of subscribers
        """
        return self.publish(pattern, message)

    def broadcast(self, message: Dict[str, Any], channel_prefix: str = "broadcast") -> int:
        """
        Broadcast to all subscribers (fanout)

        Args:
            message: Message dict
            channel_prefix: Broadcast channel name

        Returns:
            Number of subscribers
        """
        return self.publish(channel_prefix, message)

    def close(self):
        """Close connection"""
        if self.redis:
            self.redis.close()


class RedisSubscriber:
    """
    Subscribe to Redis channels
    Real-time message listening
    """

    def __init__(self, redis_client: redis.Redis = None, host: str = "localhost", port: int = 6379):
        """
        Initialize Redis subscriber

        Args:
            redis_client: Redis client (or create from host/port)
            host: Redis host
            port: Redis port
        """
        self.redis = redis_client or redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5
        )

    def subscribe(self, channels: list[str] = None, patterns: list[str] = None):
        """
        Subscribe to channels or patterns

        Args:
            channels: List of exact channel names
            patterns: List of patterns (wildcard *?)

        Yields:
            Messages received
        """
        pubsub = self.redis.pubsub()

        # Subscribe to exact channels
        if channels:
            pubsub.subscribe(*channels)
            logger.info(f"Subscribed to channels: {channels}")

        # Subscribe to patterns
        if patterns:
            pubsub.psubscribe(*patterns)
            logger.info(f"Subscribed to patterns: {patterns}")

        try:
            for message in pubsub.listen():
                if message['type'] in ('message', 'pmessage'):
                    try:
                        data = json.loads(message['data'])
                        yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message: {message['data']}")
                        yield {"raw": message['data']}
        except Exception as e:
            logger.error(f"Error in subscribe: {e}")
        finally:
            pubsub.close()

    def subscribe_single(self, channel: str, callback=None):
        """
        Subscribe to single channel (blocking)

        Args:
            channel: Channel name
            callback: Callback function for each message
        """
        pubsub = self.redis.pubsub()
        pubsub.subscribe(channel)
        logger.info(f"Subscribed to {channel}")

        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        if callback:
                            callback(data)
                        else:
                            logger.info(f"Received: {data}")
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message: {message['data']}")
        finally:
            pubsub.close()

    def close(self):
        """Close connection"""
        if self.redis:
            self.redis.close()


class RedisStream:
    """
    Redis Streams (consumer groups, durable queues)
    Use for message queues with consumer groups
    """

    def __init__(self, redis_client: redis.Redis = None, host: str = "localhost", port: int = 6379):
        """
        Initialize Redis Stream manager

        Args:
            redis_client: Redis client
            host: Redis host
            port: Redis port
        """
        self.redis = redis_client or redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )

    def add_message(self, stream: str, message: Dict[str, Any]) -> str:
        """
        Add message to stream

        Args:
            stream: Stream name
            message: Message dict

        Returns:
            Message ID
        """
        try:
            msg_id = self.redis.xadd(stream, message)
            logger.info(f"Added to stream {stream}: {msg_id}")
            return msg_id
        except Exception as e:
            logger.error(f"Failed to add to stream: {e}")
            raise

    def create_consumer_group(self, stream: str, group: str, id: str = "0"):
        """
        Create consumer group

        Args:
            stream: Stream name
            group: Group name
            id: Starting ID (0 = from beginning, $ = new messages only)
        """
        try:
            self.redis.xgroup_create(stream, group, id=id, mkstream=True)
            logger.info(f"Created consumer group {group} on {stream}")
        except redis.ResponseError:
            logger.debug(f"Group {group} already exists")

    def read_group(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 1,
        block_ms: int = 1000
    ):
        """
        Read from consumer group (blocking)

        Args:
            stream: Stream name
            group: Group name
            consumer: Consumer name
            count: Messages per read
            block_ms: Block timeout

        Yields:
            (message_id, message_data) tuples
        """
        while True:
            try:
                messages = self.redis.xreadgroup(
                    {stream: ">"},
                    group,
                    consumer,
                    count=count,
                    block=block_ms,
                    noack=False
                )

                if messages:
                    for stream_name, message_list in messages:
                        for msg_id, data in message_list:
                            yield msg_id, data
            except Exception as e:
                logger.error(f"Error reading from group: {e}")
                raise

    def acknowledge(self, stream: str, group: str, message_id: str):
        """
        Acknowledge message (mark as processed)

        Args:
            stream: Stream name
            group: Group name
            message_id: Message ID to acknowledge
        """
        try:
            self.redis.xack(stream, group, message_id)
            logger.debug(f"Acknowledged {message_id}")
        except Exception as e:
            logger.error(f"Failed to acknowledge: {e}")

    def close(self):
        """Close connection"""
        if self.redis:
            self.redis.close()


# Factories
_publisher_instance = None
_subscriber_instance = None
_stream_instance = None


def get_redis_publisher(redis_client: redis.Redis = None) -> RedisPublisher:
    """Get or create publisher instance"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = RedisPublisher(redis_client)
    return _publisher_instance


def get_redis_subscriber(redis_client: redis.Redis = None) -> RedisSubscriber:
    """Get or create subscriber instance"""
    global _subscriber_instance
    if _subscriber_instance is None:
        _subscriber_instance = RedisSubscriber(redis_client)
    return _subscriber_instance


def get_redis_stream(redis_client: redis.Redis = None) -> RedisStream:
    """Get or create stream instance"""
    global _stream_instance
    if _stream_instance is None:
        _stream_instance = RedisStream(redis_client)
    return _stream_instance
