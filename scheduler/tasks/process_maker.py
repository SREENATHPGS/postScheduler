from scheduler import celery
from scheduler.db import get_db
from datetime import datetime
import multiprocessing

def schedulerProcessFn():
    pass




@celery.task()
def create_processes():
    print("Forking every minute.")
    db = get_db()
    # db.row_factory = dict_factory
    posts = db.execute('SELECT * FROM post WHERE post_status =?',("saved",)).fetchall()
    for post in posts:
        date = datetime.strptime(post["date"], '%d-%m-%Y:%H:%M:%S') #12-04-2020:23:30:00
        print(date, datetime.now())
        tDiff = int(((date - datetime.now()).total_seconds())/60)
        if -5 <= tDiff <= 5:
            print("placing task.")
            schedulerProcess = multiprocessing.Process(name = "schedulerProcess", target = schedulerProcessFn)


