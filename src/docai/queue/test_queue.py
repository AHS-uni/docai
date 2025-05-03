from docai.queue.service import QueueService

q_service = QueueService()

queue_name = "test"

items = [
    {"task_id": "t1", "foo": "bar"},
    {"task_id": "t2", "foo": "baz"},
]

q_service.enqueue_batch(queue_name, items)
print(f"Enqueued {len(items)} items")

fetched = q_service.fetch_batch(queue_name, batch_size=10, wait_seconds=1)
print(f"Fetched {len(fetched)} items:")
for msg in fetched:
    print(" ", msg["task_id"], msg["payload"])

receipts = [msg["receipt"] for msg in fetched]
q_service.ack(queue_name, receipts)
print("Acknowledged all fetched items")

leftovers = q_service.fetch_batch(queue_name, batch_size=1, wait_seconds=0)
print("Left in queue after ack:", len(leftovers))
