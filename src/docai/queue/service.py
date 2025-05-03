"""
Provides a generic QueueService implementation using Kombu as the broker client.
"""

import logging
from typing import Any, Dict, List, Optional

from kombu import Connection, Exchange, Producer
from kombu.entity import Queue as KombuQueue
from kombu.exceptions import OperationalError, TimeoutError, Empty

from .config import BROKER_URL, DEFAULT_QUEUES, PREFETCH_COUNT, VISIBILITY_TIMEOUT
from .exceptions import (
    AckError,
    EnqueueError,
    FetchError,
    InvalidQueueNameError,
    NackError,
    ConnectionError,
)

logger = logging.getLogger(__name__)


class QueueService:
    """
    A Kombu-based queue service for producing and consuming JSON-serializable
    messages across multiple logical queues, using low-level Producer for
    publishing and the simple interface for consumption.
    """

    def __init__(
        self, broker_url: Optional[str] = None, exchange_type: str = "direct"
    ) -> None:
        """
        Initialize a QueueService.

        Args:
            broker_url: Broker URL (e.g. amqp://, redis://). Defaults to BROKER_URL.
            exchange_type: AMQP exchange type (e.g. 'direct', 'topic').
        """
        self.broker_url = broker_url or BROKER_URL
        self.exchange_type = exchange_type
        self.connection = Connection(self.broker_url)

    def _validate_queue(self, queue_name: str) -> None:
        """
        Validate that queue_name exists in DEFAULT_QUEUES.

        Raises:
            InvalidQueueNameError: If queue_name is not whitelisted.
        """
        if queue_name not in DEFAULT_QUEUES:
            logger.error("Queue '%s' is not whitelisted", queue_name)
            raise InvalidQueueNameError(queue_name)

    def _ensure_connection(self) -> None:
        """
        Ensure an active broker connection, retrying on failure.

        Raises:
            ConnectionError: If unable to connect after retries.
        """
        try:
            self.connection.ensure_connection(
                max_retries=3,
                interval_start=0.2,
                errback=lambda exc, _: logger.warning("Reconnect failed: %s", exc),
            )
        except OperationalError as exc:
            logger.exception("Could not connect to broker: %s", exc)
            raise ConnectionError(f"Broker connection failed: {exc}")

    def enqueue_batch(self, queue_name: str, items: List[Dict[str, Any]]) -> None:
        """
        Publish a batch of payload dictionaries to the given queue.

        Args:
            queue_name: Logical queue to send messages to.
            items: List of JSON-serializable dicts.

        Raises:
            InvalidQueueNameError: If queue_name invalid.
            ConnectionError: On broker connection issues.
            EnqueueError: If publish fails for any item.
        """
        self._validate_queue(queue_name)
        self._ensure_connection()

        exchange = Exchange(queue_name, type=self.exchange_type, durable=True)
        queue_entity = KombuQueue(
            queue_name,
            exchange,
            routing_key=queue_name,
            durable=True,
        )
        retry_policy = {
            "interval_start": 0,
            "interval_step": 2,
            "interval_max": 30,
            "max_retries": 5,
        }

        channel = None
        try:
            channel = self.connection.channel()
            producer = Producer(
                channel,
                serializer="json",
                auto_declare=False,
            )
            for item in items:
                try:
                    producer.publish(
                        item,
                        exchange=exchange,
                        routing_key=queue_name,
                        declare=[exchange, queue_entity],
                        retry=True,
                        retry_policy=retry_policy,
                    )
                except Exception as exc:
                    logger.exception("Error enqueuing to '%s': %s", queue_name, exc)
                    raise EnqueueError(f"Error enqueuing to {queue_name}: {exc}")
                logger.info("Enqueued %d messages to '%s'", len(items), queue_name)
        except OperationalError as exc:
            logger.exception("Broker operational error: %s", exc)
            raise ConnectionError(f"Broker operational error: {exc}")
        finally:
            if channel is not None:
                try:
                    channel.close()
                except Exception:
                    logger.warning("Failed to close channel for '%s'", queue_name)

    def fetch_batch(
        self, queue_name: str, batch_size: int, wait_seconds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve up to `batch_size` messages from the specified queue,
        waiting up to `wait_seconds` for the first.

        Uses Kombu's SimpleQueue for consumer simplicity.

        Args:
            queue_name: Logical queue name.
            batch_size: Maximum messages to fetch.
            wait_seconds: Timeout for first message; defaults to VISIBILITY_TIMEOUT.

        Returns:
            List of dicts with keys:
              - 'task_id': Optional identifier from payload
              - 'payload': Full message body dict
              - 'receipt': Message object for ack/nack

        Raises:
            InvalidQueueNameError: If queue_name invalid.
            ConnectionError: On broker connection issues.
            FetchError: On consumer or timeout errors.
        """
        self._validate_queue(queue_name)
        self._ensure_connection()

        timeout = wait_seconds or VISIBILITY_TIMEOUT
        messages: List[Dict[str, Any]] = []

        try:
            simple_queue = self.connection.SimpleQueue(queue_name, no_ack=False)
        except Exception as exc:
            logger.exception("Could not open queue '%s': %s", queue_name, exc)
            raise FetchError(f"Open queue error: {exc}")

        # Apply QoS via underlying consumer
        try:
            simple_queue.consumer.qos(prefetch_count=PREFETCH_COUNT)
        except Exception as exc:
            logger.warning("QoS not applied to '%s': %s", queue_name, exc)

        try:
            for _ in range(batch_size):
                try:
                    msg = simple_queue.get(block=True, timeout=timeout)
                except TimeoutError:
                    break
                except Empty:
                    break
                except Exception as exc:
                    logger.exception("Error fetching from '%s': %s", queue_name, exc)
                    raise FetchError(f"Error fetching message: {exc}")

                body = msg.payload
                task_id = body.get("task_id")
                messages.append(
                    {
                        "task_id": task_id,
                        "payload": body,
                        "receipt": msg,
                    }
                )

            logger.info("Fetched %d messages from '%s'", len(messages), queue_name)
            return messages

        finally:
            try:
                simple_queue.close()
            except Exception:
                logger.warning("Failed to close SimpleQueue for '%s'", queue_name)

    def ack(self, queue_name: str, receipts: List[Any]) -> None:
        """
        Acknowledge successful processing of messages.

        Args:
            queue_name: Logical queue name.
            receipts: List of Message objects from fetch_batch.

        Raises:
            InvalidQueueNameError: If queue_name invalid.
            ConnectionError: On broker connection issues.
            AckError: If ack fails.
        """
        self._validate_queue(queue_name)
        self._ensure_connection()

        errors: List[Exception] = []
        for msg in receipts:
            try:
                msg.ack()
            except Exception as exc:
                logger.exception("Ack failed for '%s': %s", queue_name, exc)
                errors.append(exc)
        if errors:
            raise AckError(f"Ack failures: {errors}")
        logger.info("Acknowledged %d messages on '%s'", len(receipts), queue_name)

    def nack(self, queue_name: str, receipts: List[Any], requeue: bool = True) -> None:
        """
        Reject messages, optionally requeuing them.

        Args:
            queue_name: Logical queue name.
            receipts: List of Message objects from fetch_batch.
            requeue: True to return to queue, False to discard.

        Raises:
            InvalidQueueNameError: If queue_name invalid.
            ConnectionError: On broker connection issues.
            NackError: If reject fails.
        """
        self._validate_queue(queue_name)
        self._ensure_connection()

        errors: List[Exception] = []
        for msg in receipts:
            try:
                msg.reject(requeue=requeue)
            except Exception as exc:
                logger.exception("Reject failed for '%s': %s", queue_name, exc)
                errors.append(exc)
        if errors:
            raise NackError(f"Reject failures: {errors}")
        logger.info(
            "Rejected %d messages on '%s' (requeue=%s)",
            len(receipts),
            queue_name,
            requeue,
        )
