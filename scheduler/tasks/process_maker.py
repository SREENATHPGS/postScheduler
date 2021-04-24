from scheduler import celery
from scheduler.db import get_db
from datetime import datetime, timezone
import billiard as multiprocessing
import requests, json, pytz, time

tzoneMap = {
    "IST" : "Asia/Calcutta"
}

def schedulerProcessFn(postObject, db):
    print(f'Posting......{postObject["id"]}')
    date = datetime.strptime(postObject["date"], '%Y-%m-%d:%H:%M:%S:%z') #12-04-2020:23:30:00:+05:30
    yetToPost = True
    while yetToPost:
        tDiff = int(((date - datetime.now(timezone.utc)).total_seconds())/60)
        if tDiff == 0:
            print("Calling instagram apis...")
            post_details = json.loads(postObject["post_details"])
            create_media_request = requests.post(f'https://graph.facebook.com/{post_details["instagram_id"]}/media?access_token={post_details["access_token"]}&image_url={postObject["media_link"]}&caption={postObject["media_story"]}')

            media_id = create_media_request.json().get("id", None)
            error = create_media_request.json().get("error", None)
            post_details["error"] = error
            

            if not error:
                post_details["ig_media_id"] = media_id

                db.execute('UPDATE post set post_details=?,post_status=? where id=?',(json.dumps(post_details), "posted", postObject["id"]))

                db.commit()
                print("Posted media successfully.")

                publish_media_request = requests.post(f'https://graph.facebook.com/{post_details["instagram_id"]}/media_publish?creation_id={post_details["ig_media_id"]}&access_token={post_details["access_token"]}')

                ig_post_id = publish_media_request.json().get("id", None)
                error = publish_media_request.json().get("error", None)
                post_details["error"] = error

                if not error:
                    post_details["ig_post_id"] = ig_post_id
                    db.execute('UPDATE post set post_details=?,post_status=? where id=?',(json.dumps(post_details), "published", postObject["id"]))
                    db.commit()

                    print("Published media successfully.")
                    yetToPost = False
                else:
                    db.execute('UPDATE post set post_details=?, post_status=? where id=?',(json.dumps(post_details) ,"failed", postObject["id"]))
                    db.commit()

                    print("Error in posting publish media.")
                    yetToPost = False
            else:
                print("Error in create media request.")
                db.execute('UPDATE post set post_details=?, post_status=? where id=?',(json.dumps(post_details) ,"failed", postObject["id"]))

                db.commit()
                yetToPost = False

@celery.task()
def create_processes():
    print("Forking every minute.")
    db = get_db()
    # db.row_factory = dict_factory
    posts = db.execute('SELECT * FROM post WHERE post_status =?',("saved",)).fetchall()
    for post in posts:
        try:
            date = post["date"]
            if time.tzname[0] == "UTC":
                date = datetime.strptime(post["date"], '%Y-%m-%d:%H:%M:%S:%z') 
                date = date.astimezone(pytz.UTC)
                print(f"Date converted to UTC as system timezone is {time.tzname}")
            print(date, datetime.now())
            tDiff = int(((date - datetime.now(timezone.utc)).total_seconds())/60)
            print(tDiff)
            if -5 <= tDiff <= 5:
                print("placing task.")
                schedulerProcess = multiprocessing.Process(name = "schedulerProcess", target = schedulerProcessFn, args = [post, db])
                db.execute('UPDATE post set post_status=? where id=?', ("processing", post["id"]))
                db.commit()
                schedulerProcess.start()
        except Exception as e:
            post_details = {"error":"Task processing failed.", "stacktrace":f"{e}"}
            db.execute('UPDATE post set post_details=?, post_status=? where id=?', (json.dumps(post_details), "failed", post["id"]))
            db.commit()
            print("Task processing failed.")
            print(e)
