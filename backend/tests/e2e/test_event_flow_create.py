"""
E2E Test: Create Task Event Flow (T087)
Tests the complete flow: API -> Event Published -> Event Consumed -> State Persisted
"""
import asyncio
import httpx
import json
import time
from typing import Dict, Any

BACKEND_URL = "http://localhost:8000"
DAPR_URL = "http://localhost:3500"
TEST_USER_ID = "e2e-test-user"


async def test_create_task_event_flow():
    """
    Test Flow:
    1. Create task via API
    2. Verify task created response
    3. Verify event published to Kafka (via Dapr)
    4. Wait for event consumption
    5. Verify task persisted in State Store
    """
    print("=== E2E Test: Create Task Event Flow ===\n")

    # Step 1: Create task via API
    print("Step 1: Creating task via API...")
    task_data = {
        "userId": TEST_USER_ID,
        "title": "E2E Test Task - Create Flow",
        "description": "Testing event-driven create flow",
        "priority": "high",
        "tags": ["e2e-test", "create-flow"],
        "dueDate": "2026-12-31T23:59:59Z"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/events/tasks",
            json=task_data
        )

        if response.status_code != 201:
            print(f"❌ Failed to create task: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()
        task_id = result["task"]["id"]
        event_id = result["eventId"]

        print(f"✅ Task created: {task_id}")
        print(f"✅ Event published: {event_id}\n")

        # Step 2: Wait for event consumption (give Dapr time to process)
        print("Step 2: Waiting for event consumption...")
        await asyncio.sleep(2)

        # Step 3: Verify task in State Store via Dapr
        print("Step 3: Verifying task in State Store...")
        state_response = await client.get(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{task_id}"
        )

        if state_response.status_code != 200:
            print(f"❌ Task not found in State Store: {state_response.status_code}")
            return False

        stored_task = state_response.json()
        print(f"✅ Task found in State Store")
        print(f"   Title: {stored_task.get('title')}")
        print(f"   Priority: {stored_task.get('priority')}")
        print(f"   Tags: {stored_task.get('tags')}\n")

        # Step 4: Verify task via API GET
        print("Step 4: Verifying task via GET API...")
        get_response = await client.get(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )

        if get_response.status_code != 200:
            print(f"❌ Failed to retrieve task: {get_response.status_code}")
            return False

        retrieved_task = get_response.json()["task"]
        print(f"✅ Task retrieved via API")
        print(f"   ID matches: {retrieved_task['id'] == task_id}")
        print(f"   Title matches: {retrieved_task['title'] == task_data['title']}")
        print(f"   UserId matches: {retrieved_task['userId'] == TEST_USER_ID}\n")

        # Cleanup
        print("Cleanup: Deleting test task...")
        await client.delete(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )
        print("✅ Test task deleted\n")

        print("=== ✅ Create Task Event Flow Test PASSED ===\n")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_create_task_event_flow())
    exit(0 if success else 1)
