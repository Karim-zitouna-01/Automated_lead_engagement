# Automated_lead_engagement/server/common/celery_config.py
from celery import Celery

celery_app = Celery(
    "lead_generator",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    imports=('server.scripts.celery_test', 'server.services.identification_service',)
)

celery_app.conf.task_routes = {
    "server.services.identification_service.generate_leads_task": {"queue": "leads"}
}


