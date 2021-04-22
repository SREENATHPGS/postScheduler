import functools

import secrets, re, datetime
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify

from werkzeug.security import check_password_hash, generate_password_hash
from scheduler.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

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


@bp.route('/user', methods=['POST'])
def createUser():
    return_data = {}
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    email = data.get('email', None)

    db = get_db()

    if not username:
        return_data["error"] = "Username is required."
        return jsonify(return_data)
    
    if db.execute('SELECT id FROM user WHERE username = ?',(username,)).fetchone() is not None:
        return_data["error"] = "username already in use."
        return jsonify(return_data)

    if not password:
        return_data["error"] = "Password is required."
        return jsonify(return_data)

    
    validationResult, validationCondition = validatePassword(password)

    if not validationResult:
        return_data["error"] = "password doesn't comply security policy."
        return_data["condition"] = validationCondition
        return jsonify(return_data)
        
    password = generate_password_hash(password)

    if not email:
        return_data["error"] = "Email is required."
        return jsonify(return_data)
    
    if db.execute('SELECT id FROM user WHERE email = ?',(email,)).fetchone() is not None:
        return_data["error"] = "email already in use."
        return jsonify(return_data)
        
    api_key = secrets.token_urlsafe(64)
    
    db.execute(
        'INSERT INTO user (username, password, api_key, email, created, updated) VALUES (?,?,?,?,?,?)', (username, password, api_key, email, datetime.datetime.now(), datetime.datetime.now())
    )

    db.commit()
    return "User created!"

@bp.route('/user/login', methods=['POST'])
def getUser():
    return_data = {}

    data = request.get_json()

    username = data.get('username', None)
    password = data.get('password', None)
    api_key = data.get('api_key', None)

    db = get_db()

    if not username:
        return_data["error"] = "Username is required."
        return jsonify(return_data)
    
    if not password:
        if not api_key:
            return_data["error"] = "Password/Api Key is required."
            return jsonify(return_data)

    user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

    if not user:
        return_data["error"] = "No such user."
        return_data["isValid"] = False
        return jsonify(return_data)
    
    if password:
        if not check_password_hash(user["password"], password):
            return_data["error"] = "Invalid user credentials."
            return jsonify(return_data)

        return_data["data"] = {"username": user["username"], "api_key": user["api_key"]}

        return jsonify(return_data)

    if user["api_key"] == api_key:
        return_data["data"] = {"username": user["username"], "api_key": user["api_key"], "isValid":True}
        return jsonify(return_data)
    elif not password:
        return_data["error"] = "Invalid user credentials."
        return_data["isValid"] = False
        return jsonify(return_data)

 