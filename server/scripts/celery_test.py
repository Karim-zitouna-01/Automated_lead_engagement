# Automated_lead_engagement/test_celery.py

from celery import shared_task
from server.common.celery_config import celery_app  # Import your main Celery app instance

# Define a simple test task
@celery_app.task  # Use the app instance to register the task
def add(x, y):
    print(f"Executing add task with arguments: {x}, {y}")
    return x + y

if __name__ == "__main__":
    print("Sending a test task to Celery...")
    result = add.delay(4, 4)
    print(f"Task ID: {result.id}")
    print("Task sent. Now, check your Celery worker console for execution.")