import functools

import secrets, re, datetime, json
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify

from werkzeug.security import check_password_hash, generate_password_hash
from scheduler.db import get_db

bp = Blueprint('schedule_post', __name__)

def validatePassword(password):
    condition  = "Minimum eight characters, at least one letter and one number."
    regexFunction = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"

    # Minimum eight characters, at least one letter, one number and one special character:
    # "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"

    #Minimum eight characters, at least one uppercase letter, one lowercase letter and one number:
    # "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"

    # Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character:
    # "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    # Minimum eight and maximum 10 characters, at least one uppercase letter, one lowercase letter, one number and one special character:
    # "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,10}$"

    if re.match(regexFunction, password):
        return True, condition
    
    return False, condition

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@bp.route('/schedule_post', methods=['POST'])
def createSchedule():
    return_data = {}
    headers = request.headers
    data = request.get_json()

    username = headers.get("SCHEDULER-USERNAME", None)
    api_key = headers.get("SCHEDULER-API-KEY", None)

    media_link = data.get('media_link', None)
    media_story = data.get('media_story', None)
    schedule_date = data.get('schedule_date', None)
    post_details = data.get('post_details', {})

    db = get_db()

    if not media_link:
        return_data["error"] = "Media Link is required."
        return jsonify(return_data)
    
    if not media_story:
        return_data["error"] = "Media story is required."
        return jsonify(return_data)

    if not username:
        return_data["error"] = "Username is required."
        return jsonify(return_data)
    
    if not api_key:
        return_data["error"] = "Api key is required."
        return jsonify(return_data)

    if not schedule_date:
        return_data["error"] = "Schedule date is required."
        return jsonify(return_data)
    
    if post_details:
        if not isinstance(post_details, dict):
            return_data["error"] = "Post details should be dict."
            return jsonify(return_data)

    
    posting_user = db.execute('SELECT id FROM user WHERE username = ? AND api_key = ?',(username,api_key,)).fetchone()

    if not posting_user:
        return_data["error"] = "no such user exists."
        return jsonify(return_data)
    
    db.execute(
        'INSERT INTO post (date, media_link, media_story, user_id, post_details, created, updated) VALUES (?,?,?,?,?,?,?)', (schedule_date, media_link, media_story, posting_user["id"], json.dumps(post_details), datetime.datetime.now(), datetime.datetime.now())
    )

    db.commit()
    return "Schedule action added to database.!"

@bp.route('/schedule_post', methods=['GET'])
def getSchedule():
    
    return_data = {}
    headers = request.headers

    username = headers.get("SCHEDULER-USERNAME", None)
    api_key = headers.get("SCHEDULER-API-KEY", None)

    db = get_db()
    db.row_factory = dict_factory

    if not username:
        return_data["error"] = "Username is required."
        return jsonify(return_data)
    
    if not api_key:
        return_data["error"] = "Api key is required."
        return jsonify(return_data)

    posting_user = db.execute('SELECT id FROM user WHERE username = ? AND api_key = ?',(username,api_key,)).fetchone()

    if not posting_user:
        return_data["error"] = "no such user exists."
        return jsonify(return_data)

    schedules = db.execute('SELECT * FROM post WHERE user_id = ?', (posting_user["id"],)).fetchall()

    # print(schedules)

    return_data["data"] = schedules

    return return_data