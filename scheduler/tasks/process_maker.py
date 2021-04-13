from scheduler import celery

@celery.task()
def create_processes():
    print("Forking every minute.")