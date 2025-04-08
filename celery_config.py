from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend= os.getenv('backend_env'),   
        broker= os.getenv('broker_env')       
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery