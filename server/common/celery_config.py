from celery import Celery

celery_app = Celery(
    "lead_generator",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_routes = {
    "server.services.identification_service.generate_leads_task": {"queue": "leads"}
}
