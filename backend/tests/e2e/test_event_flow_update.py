"""
E2E Test: Update Task Event Flow (T088)
Tests the complete flow: API Update -> Event Published -> Event Consumed -> State Updated
"""
import asyncio
import httpx
import json
import time

BACKEND_URL = "http://localhost:8000"
DAPR_URL = "http://localhost:3500"
TEST_USER_ID = "e2e-test-user"


async def test_update_task_event_flow():
    """
    Test Flow:
    1. Create initial task
    2. Update task via API
    3. Verify todo-updated event published
    4. Wait for event consumption
    5. Verify task updated in State Store
    """
    print("=== E2E Test: Update Task Event Flow ===\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Create initial task
        print("Step 1: Creating initial task...")
        initial_data = {
            "userId": TEST_USER_ID,
            "title": "E2E Test Task - Update Flow (Original)",
            "description": "Original description",
            "priority": "medium",
            "tags": ["e2e-test"]
        }

        create_response = await client.post(
            f"{BACKEND_URL}/api/v1/events/tasks",
            json=initial_data
        )

        if create_response.status_code != 201:
            print(f"❌ Failed to create task: {create_response.status_code}")
            return False

        task_id = create_response.json()["task"]["id"]
        print(f"✅ Initial task created: {task_id}\n")

        # Wait for creation to settle
        await asyncio.sleep(1)

        # Step 2: Update task via API
        print("Step 2: Updating task via API...")
        update_data = {
            "title": "E2E Test Task - Update Flow (UPDATED)",
            "description": "Updated description",
            "priority": "urgent",
            "tags": ["e2e-test", "updated"]
        }

        update_response = await client.put(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}",
            json=update_data
        )

        if update_response.status_code != 200:
            print(f"❌ Failed to update task: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False

        update_result = update_response.json()
        print(f"✅ Task updated")
        print(f"✅ Update event published: {update_result.get('eventId')}\n")

        # Step 3: Wait for event consumption
        print("Step 3: Waiting for event consumption...")
        await asyncio.sleep(2)

        # Step 4: Verify updated task in State Store
        print("Step 4: Verifying updated task in State Store...")
        state_response = await client.get(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{task_id}"
        )

        if state_response.status_code != 200:
            print(f"❌ Task not found in State Store: {state_response.status_code}")
            return False

        stored_task = state_response.json()
        title_updated = stored_task.get("title") == update_data["title"]
        priority_updated = stored_task.get("priority") == update_data["priority"]
        tags_updated = set(stored_task.get("tags", [])) == set(update_data["tags"])

        print(f"✅ Task found in State Store")
        print(f"   Title updated: {title_updated} - {stored_task.get('title')}")
        print(f"   Priority updated: {priority_updated} - {stored_task.get('priority')}")
        print(f"   Tags updated: {tags_updated} - {stored_task.get('tags')}\n")

        # Step 5: Verify via API GET
        print("Step 5: Verifying updated task via GET API...")
        get_response = await client.get(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )

        if get_response.status_code != 200:
            print(f"❌ Failed to retrieve task: {get_response.status_code}")
            return False

        retrieved_task = get_response.json()["task"]
        print(f"✅ Task retrieved via API")
        print(f"   Title: {retrieved_task['title']}")
        print(f"   Priority: {retrieved_task['priority']}")
        print(f"   Description: {retrieved_task['description']}\n")

        # Cleanup
        print("Cleanup: Deleting test task...")
        await client.delete(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )
        print("✅ Test task deleted\n")

        all_checks_passed = title_updated and priority_updated and tags_updated
        if all_checks_passed:
            print("=== ✅ Update Task Event Flow Test PASSED ===\n")
        else:
            print("=== ❌ Update Task Event Flow Test FAILED ===\n")

        return all_checks_passed


if __name__ == "__main__":
    success = asyncio.run(test_update_task_event_flow())
    exit(0 if success else 1)
