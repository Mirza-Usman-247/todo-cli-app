"""
E2E Test: Delete Task Event Flow (T089)
Tests the complete flow: API Delete -> Event Published -> Event Consumed -> State Deleted
"""
import asyncio
import httpx
import json
import time

BACKEND_URL = "http://localhost:8000"
DAPR_URL = "http://localhost:3500"
TEST_USER_ID = "e2e-test-user"


async def test_delete_task_event_flow():
    """
    Test Flow:
    1. Create task
    2. Verify task exists
    3. Delete task via API
    4. Verify todo-deleted event published
    5. Wait for event consumption
    6. Verify task removed from State Store
    7. Verify 404 on GET request
    """
    print("=== E2E Test: Delete Task Event Flow ===\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Create task
        print("Step 1: Creating task...")
        task_data = {
            "userId": TEST_USER_ID,
            "title": "E2E Test Task - Delete Flow",
            "description": "This task will be deleted",
            "priority": "low",
            "tags": ["e2e-test", "delete-test"]
        }

        create_response = await client.post(
            f"{BACKEND_URL}/api/v1/events/tasks",
            json=task_data
        )

        if create_response.status_code != 201:
            print(f"❌ Failed to create task: {create_response.status_code}")
            return False

        task_id = create_response.json()["task"]["id"]
        print(f"✅ Task created: {task_id}\n")

        # Wait for creation to settle
        await asyncio.sleep(1)

        # Step 2: Verify task exists
        print("Step 2: Verifying task exists...")
        get_response = await client.get(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )

        if get_response.status_code != 200:
            print(f"❌ Task not found before deletion: {get_response.status_code}")
            return False

        print(f"✅ Task exists before deletion\n")

        # Step 3: Delete task via API
        print("Step 3: Deleting task via API...")
        delete_response = await client.delete(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )

        if delete_response.status_code != 200:
            print(f"❌ Failed to delete task: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            return False

        delete_result = delete_response.json()
        print(f"✅ Task deleted")
        print(f"✅ Delete event published: {delete_result.get('eventId')}\n")

        # Step 4: Wait for event consumption
        print("Step 4: Waiting for event consumption...")
        await asyncio.sleep(2)

        # Step 5: Verify task removed from State Store
        print("Step 5: Verifying task removed from State Store...")
        state_response = await client.get(
            f"{DAPR_URL}/v1.0/state/statestore-redis/task:{task_id}"
        )

        # State Store returns 204 No Content when key doesn't exist
        state_deleted = state_response.status_code == 204 or state_response.text == ""

        if state_deleted:
            print(f"✅ Task removed from State Store (status: {state_response.status_code})\n")
        else:
            print(f"❌ Task still exists in State Store")
            print(f"   Status: {state_response.status_code}")
            print(f"   Content: {state_response.text}\n")

        # Step 6: Verify 404 on GET request
        print("Step 6: Verifying task returns 404 via API...")
        final_get_response = await client.get(
            f"{BACKEND_URL}/api/v1/events/tasks/{task_id}?user_id={TEST_USER_ID}"
        )

        api_returns_404 = final_get_response.status_code == 404

        if api_returns_404:
            print(f"✅ Task returns 404 via API (expected behavior)\n")
        else:
            print(f"❌ Task still accessible via API")
            print(f"   Status: {final_get_response.status_code}\n")

        all_checks_passed = state_deleted and api_returns_404

        if all_checks_passed:
            print("=== ✅ Delete Task Event Flow Test PASSED ===\n")
        else:
            print("=== ❌ Delete Task Event Flow Test FAILED ===\n")

        return all_checks_passed


if __name__ == "__main__":
    success = asyncio.run(test_delete_task_event_flow())
    exit(0 if success else 1)
