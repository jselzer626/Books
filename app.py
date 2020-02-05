import os
import requests
import json

from flask import Flask, session, request, render_template, redirect, jsonify
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

#functions that I created locally
from helpers import login_required

app = Flask(__name__)

@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem & reload templates when changed
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['DEBUG'] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()

Session(app)


# Set up database
engine = create_engine("postgres://lowtkihiopplqx:c294ea36e059e381fcc923e236896860d16d682c459290e1bdd1ef4de4dc4dc5@ec2-174-129-255-15.compute-1.amazonaws.com:5432/d39970tuquglom")
db = scoped_session(sessionmaker(bind=engine))

#API Key for retrieving goodreads data:
goodreads_api_key = "Cel4Ud7r1ZN8Z5H8ELYmuQ"

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user_info = db.execute("SELECT * FROM users WHERE username=:username", {"username": request.form.get("username")}).fetchall()

        #check to see if username is in database
        if len(user_info) != 1 or not check_password_hash(user_info[0]["password"], request.form.get("password")):
            return render_template("login.html", message="Incorrect username or password")
        #if so then log user in and redirect to homepage
        else:
            session["user_id"] = user_info[0][0]
            session["username"] = user_info[0][1]

            return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        #check to see if username already taken, use COUNT
        if db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).rowcount == 0:

            db.execute("INSERT INTO users (username, password) VALUES (:username, :password_hash)", {"username": username, "password_hash": password_hash})
            db.commit()

            #log newly registered user in
            user_id = db.execute("SELECT userid FROM users WHERE username=:username", {"username": username}).fetchone()[0]
            session["user_id"] = user_id
            session["username"] = username

            #direct user to homepage now that logged in
            return redirect("/")

        # if user name already taken, take user back to register page and display error message
        else:
            return render_template("register.html", message="Username already taken")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()

    return redirect("/")

@app.route("/retrieve_reviews", methods=["GET"])
@login_required
def retrieve_reviews():

    reviews = db.execute("SELECT * FROM books JOIN reviews ON reviews.isbn = books.isbn WHERE reviews.username=:username", {"username": session["username"]}).fetchall()

    return render_template("reviews_summary.html", reviews=[dict(review) for review in reviews])

@app.route("/search", methods=["GET", "POST"])
@login_required
def searchbooks():
    if request.method == "GET":

        return render_template("search.html")

    if request.method == "POST":

        lookup_item = request.form.get("info")

        #case-sensitive LIKE queries
        results = db.execute(f"SELECT * FROM books WHERE title LIKE '%{lookup_item}%' OR author LIKE '%{lookup_item}%' OR isbn LIKE '%{lookup_item}%'").fetchall()

        if results:
            results_final = [dict(result) for result in results]
            return render_template("search.html", results=results_final)
        else:
            return render_template("search.html", message="No matching books found")

@app.route("/bookdetails", methods=["GET"])
@login_required
def find_details():
    if request.method == "GET":

        book_to_lookup = request.args.get("q")

        # retrieve any existing reviews as well as book details ()
        internal_review_details = db.execute("SELECT * FROM books JOIN reviews ON reviews.isbn = books.isbn WHERE books.isbn=:book_to_lookup", {"book_to_lookup": book_to_lookup}).fetchall()
        goodreads_details = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_api_key, "isbns": book_to_lookup}).json()["books"][0]

        if internal_review_details:
            review_details_final = [dict(row) for row in internal_review_details]

            return render_template("details.html", review_details_final=review_details_final, goodreads_details=goodreads_details)
        #if no reviews then just query db for general book info
        else:
            review_details_final = [dict(row) for row in db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": book_to_lookup}).fetchall()]
            return render_template("details.html", review_details_final=review_details_final, goodreads_details=goodreads_details)

@app.route("/check_reviews", methods=["GET"])
@login_required
def check_reviews():
    if request.method == "GET":

        isbn_to_check = request.args.get("isbn")

        review_details = db.execute("SELECT username FROM reviews WHERE isbn=:isbn_to_check", {"isbn_to_check": isbn_to_check}).fetchall()

        review_details_clean = [str(item).strip("'(,)'") for item in review_details]

        if session['username'] in review_details_clean:
            return jsonify(True)
        else:
            return jsonify(False)

@app.route("/submit_review", methods=["POST"])
@login_required
def submit_review():
    if request.method == "POST":

        #since rating is a radio button can't include with my dict comp below
        book_rating = request.form["book_rating"]
        review_to_upload = {item: request.form.get(item) for item in ["review_isbn", "review_text", "review_title"]}

        db.execute("INSERT INTO reviews (isbn, rating, review, username) VALUES (:isbn, :rating, :review, :username)", {"isbn": review_to_upload["review_isbn"], "rating": book_rating,
        "review": review_to_upload["review_text"], "username": session["username"]})

        db.commit()

        return render_template("index.html", success_message=f"Review for {review_to_upload['review_title']} successfully added!")

@app.route("/api/<isbn>")
@login_required
def api(isbn):

    return_details = ["title", "author", "year", "isbn", "reviews_count", "average_rating"]

    book_details = dict(db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchall()[0])
    goodreads_details = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_api_key, "isbns": isbn}).json()["books"][0]

    book_details.update(goodreads_details)

    return jsonify({detail: book_details[detail] for detail in return_details})

if __name__ == '__main__':
 app.debug = True
 port = int(os.environ.get('PORT', 5000))
 app.run(host='0.0.0.0', port=port)
