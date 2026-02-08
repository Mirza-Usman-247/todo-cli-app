"""
Load Testing with Locust (T130, T131)
Simulates concurrent users creating, updating, and deleting tasks
"""
from locust import HttpUser, task, between
import random
import uuid
import json


class TodoAppUser(HttpUser):
    """
    Simulates a user interacting with the Todo App API
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a user starts"""
        self.user_id = f"load-test-user-{uuid.uuid4().hex[:8]}"
        self.created_tasks = []

    @task(10)  # Weight: 10 (most common operation)
    def create_task(self):
        """Create a new task"""
        task_data = {
            "userId": self.user_id,
            "title": f"Load Test Task {uuid.uuid4().hex[:8]}",
            "description": "Created during load testing",
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "tags": random.sample(["test", "load", "performance", "stress"], k=random.randint(1, 3)),
            "dueDate": "2026-12-31T23:59:59Z"
        }

        with self.client.post(
            "/api/v1/events/tasks",
            json=task_data,
            catch_response=True,
            name="Create Task"
        ) as response:
            if response.status_code == 201:
                task_id = response.json().get("task", {}).get("id")
                if task_id:
                    self.created_tasks.append(task_id)
                response.success()
            else:
                response.failure(f"Failed to create task: {response.status_code}")

    @task(5)  # Weight: 5
    def list_tasks(self):
        """List tasks for user"""
        with self.client.get(
            f"/api/v1/events/tasks?user_id={self.user_id}",
            catch_response=True,
            name="List Tasks"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list tasks: {response.status_code}")

    @task(7)  # Weight: 7
    def update_task(self):
        """Update an existing task"""
        if not self.created_tasks:
            return

        task_id = random.choice(self.created_tasks)
        update_data = {
            "title": f"Updated Task {uuid.uuid4().hex[:8]}",
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "description": "Updated during load testing"
        }

        with self.client.put(
            f"/api/v1/events/tasks/{task_id}?user_id={self.user_id}",
            json=update_data,
            catch_response=True,
            name="Update Task"
        ) as response:
            if response.status_code in [200, 404]:  # 404 if task was deleted
                response.success()
            else:
                response.failure(f"Failed to update task: {response.status_code}")

    @task(3)  # Weight: 3
    def get_task(self):
        """Get a specific task"""
        if not self.created_tasks:
            return

        task_id = random.choice(self.created_tasks)

        with self.client.get(
            f"/api/v1/events/tasks/{task_id}?user_id={self.user_id}",
            catch_response=True,
            name="Get Task"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to get task: {response.status_code}")

    @task(2)  # Weight: 2
    def complete_task(self):
        """Mark a task as complete"""
        if not self.created_tasks:
            return

        task_id = random.choice(self.created_tasks)

        with self.client.patch(
            f"/api/v1/events/tasks/{task_id}/complete?user_id={self.user_id}",
            catch_response=True,
            name="Complete Task"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to complete task: {response.status_code}")

    @task(1)  # Weight: 1 (least common)
    def delete_task(self):
        """Delete a task"""
        if not self.created_tasks:
            return

        task_id = self.created_tasks.pop(random.randint(0, len(self.created_tasks) - 1))

        with self.client.delete(
            f"/api/v1/events/tasks/{task_id}?user_id={self.user_id}",
            catch_response=True,
            name="Delete Task"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to delete task: {response.status_code}")

    @task(2)  # Weight: 2
    def search_tasks(self):
        """Search tasks"""
        search_data = {
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "tags": random.sample(["test", "load", "performance"], k=1)
        }

        with self.client.post(
            "/api/v1/events/tasks/search",
            json=search_data,
            catch_response=True,
            name="Search Tasks"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to search tasks: {response.status_code}")


class TodoAppStressUser(HttpUser):
    """
    High-intensity stress testing user
    Minimal wait time, maximum operations
    """
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.user_id = f"stress-test-user-{uuid.uuid4().hex[:8]}"
        self.created_tasks = []

    @task
    def rapid_create(self):
        """Rapidly create tasks"""
        task_data = {
            "userId": self.user_id,
            "title": f"Stress Test {uuid.uuid4().hex[:8]}",
            "priority": "high",
            "tags": ["stress"]
        }

        response = self.client.post("/api/v1/events/tasks", json=task_data)
        if response.status_code == 201:
            task_id = response.json().get("task", {}).get("id")
            if task_id and len(self.created_tasks) < 100:  # Limit to 100 tasks
                self.created_tasks.append(task_id)
