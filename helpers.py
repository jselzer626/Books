import os
import requests
import json

from flask import redirect, render_template, request, session
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = "postgres://lowtkihiopplqx:c294ea36e059e381fcc923e236896860d16d682c459290e1bdd1ef4de4dc4dc5@ec2-174-129-255-15.compute-1.amazonaws.com:5432/d39970tuquglom"
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    #Decorate routes to require login.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
