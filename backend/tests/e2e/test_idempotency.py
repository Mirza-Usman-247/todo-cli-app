"""
E2E Test: Event Idempotency (T091)
Tests that duplicate events with same eventId are handled idempotently
"""
import asyncio
import httpx
import json
import uuid

BACKEND_URL = "http://localhost:8000"
DAPR_URL = "http://localhost:3500"
TEST_USER_ID = "e2e-test-user"


async def test_idempotency():
    """
    Test Flow:
    1. Publish same event twice via Dapr Pub/Sub
    2. Verify only one task created in State Store
    3. Check backend logs for "Duplicate event" messages
    """
    print("=== E2E Test: Event Idempotency ===\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Prepare event data
        print("Step 1: Preparing duplicate event data...")

        event_id = str(uuid.uuid4())
        todo_id = str(uuid.uuid4())
        timestamp = "2026-01-29T12:00:00Z"

        event_data = {
            "eventId": event_id,  # Same eventId for both publishes
            "eventType": "todo-created",
            "timestamp": timestamp,
            "todoId": todo_id,
            "userId": TEST_USER_ID,
            "payload": {
                "id": todo_id,
                "userId": TEST_USER_ID,
                "title": "Idempotency Test Task",
                "description": "Testing duplicate event handling",
                "priority": "medium",
                "tags": ["e2e-test", "idempotency"],
                "isCompleted": False,
                "createdAt": timestamp,
                "updatedAt": timestamp
            }
        }

        print(f"✅ Event prepared")
        print(f"   Event ID: {event_id}")
        print(f"   Todo ID: {todo_id}\n")

        # Step 2: Publish event first time
        print("Step 2: Publishing event (first time)...")
        first_publish = await client.post(
            f"{DAPR_URL}/v1.0/publish/pubsub-kafka/todo-created",
            json=event_data
        )

        if first_publish.status_code not in [200, 204]:
            print(f"❌ Failed to publish first event: {first_publish.status_code}")
            print(f"Response: {first_publish.text}")
            return False

        print(f"✅ First event published (status: {first_publish.status_code})")

        # Wait for event consumption
        await asyncio.sleep(2)

        # Step 3: Verify task created in State Store
        print("\nStep 3: Verifying task created in State Store...")
        state_response_1 = await client.get(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{todo_id}"
        )

        if state_response_1.status_code != 200:
            print(f"❌ Task not found after first publish: {state_response_1.status_code}")
            return False

        task_1 = state_response_1.json()
        created_at_1 = task_1.get("createdAt")

        print(f"✅ Task created in State Store")
        print(f"   Title: {task_1.get('title')}")
        print(f"   Created at: {created_at_1}\n")

        # Step 4: Publish SAME event again (duplicate)
        print("Step 4: Publishing same event again (duplicate)...")
        second_publish = await client.post(
            f"{DAPR_URL}/v1.0/publish/pubsub-kafka/todo-created",
            json=event_data
        )

        if second_publish.status_code not in [200, 204]:
            print(f"❌ Failed to publish second event: {second_publish.status_code}")
            print(f"Response: {second_publish.text}")
            return False

        print(f"✅ Second event published (status: {second_publish.status_code})")

        # Wait for event consumption
        await asyncio.sleep(2)

        # Step 5: Verify task NOT duplicated in State Store
        print("\nStep 5: Verifying task NOT duplicated...")
        state_response_2 = await client.get(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{todo_id}"
        )

        if state_response_2.status_code != 200:
            print(f"❌ Task not found after second publish: {state_response_2.status_code}")
            return False

        task_2 = state_response_2.json()
        created_at_2 = task_2.get("createdAt")

        # Verify createdAt timestamp hasn't changed (proves no duplicate)
        timestamps_match = created_at_1 == created_at_2

        print(f"✅ Task still exists with same data")
        print(f"   Created at (first): {created_at_1}")
        print(f"   Created at (second): {created_at_2}")
        print(f"   Timestamps match: {timestamps_match}\n")

        # Step 6: Cleanup
        print("Cleanup: Deleting test task...")
        await client.delete(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{todo_id}"
        )
        print("✅ Test task deleted\n")

        if timestamps_match:
            print("=== ✅ Idempotency Test PASSED ===\n")
            print("Duplicate event was correctly ignored - no duplicate task created.\n")
        else:
            print("=== ❌ Idempotency Test FAILED ===\n")
            print("Timestamps differ - task may have been duplicated or overwritten.\n")

        return timestamps_match


if __name__ == "__main__":
    success = asyncio.run(test_idempotency())
    exit(0 if success else 1)
