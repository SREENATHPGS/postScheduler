from scheduler import celery
from scheduler.db import get_db
from datetime import datetime
import billiard as multiprocessing
import requests

def schedulerProcessFn(postObject, db):
    print(f'Posting......{postObject["id"]}')
    date = datetime.strptime(postObject["date"], '%d-%m-%Y:%H:%M:%S') #12-04-2020:23:30:00
    yetToPost = True
    while yetToPost:
        tDiff = int(((date - datetime.now()).total_seconds())/60)
        if tDiff == 0:
            print("Calling instagram apis...")
            create_media_reuest = requests.post(f'https://graph.facebook.com/{postObject["post_details"]["instagram_id"]}/media?
            access_token={postObject["post_details"]["access_token"]}&caption={postObject["media_story"]}')

            media_id = create_media_request.json().get("id", None)
            error = create_media_request.json().get("error", None)
            postObject["post_details"]["error"] = error


            if not error:
                postObject["post_details"]["ig_media_id"] = media_id

                db.execute('UPDATE post set post_details=?,post_status=? where id=?',(postObject["post_details"], "posted", postObject["id"]))

                publish_media_request = requests.post(f'https://graph.facebook.com/{postObject["post_details"]["instagram_id"]}/publish_media?creation_id={postObject["post_details"]["ig_media_id"]}&access_token={postObject["post_details"]["access_token"]}')

                ig_post_id = publish_media_request.json().get("id", None)
                error = publish_media_request.json().get("error", None)
                postObject["post_details"]["error"] = error

                if not error:
                    postObject["post_details"]["ig_post_id"] = ig_post_id
                    db.execute('UPDATE post set post_details=?,post_status=? where id=?',(postObject["post_details"], "published", postObject["id"]))

                    yetToPost = False
                else:
                    db.execute('UPDATE post set post_details=?, post_status=? where id=?',(postObject["post_details"] ,"failed", postObject["id"]))

                    print("Error in posting publish media.")
                
            else:
                print("Error in create media request.")
                db.execute('UPDATE post set post_details=?, post_status=? where id=?',(postObject["post_details"] ,"failed", postObject["id"]))



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
            schedulerProcess = multiprocessing.Process(name = "schedulerProcess", target = schedulerProcessFn, args = [post, db])
            schedulerProcess.start()


