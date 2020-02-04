import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://lowtkihiopplqx:c294ea36e059e381fcc923e236896860d16d682c459290e1bdd1ef4de4dc4dc5@ec2-174-129-255-15.compute-1.amazonaws.com:5432/d39970tuquglom")
db = scoped_session(sessionmaker(bind=engine))

with open('books.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": row["isbn"], "title": row["title"], "author": row["author"], "year":row["year"]})
        db.commit()
