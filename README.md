# Project 1

JLS Book Review is a flask program that allows users to access book information from a searchable database, and leave reviews for selected books.

For a selected book, this program displays details such as title, isbn, author and year of publication (provided in a csv file with the project source code)
as well as information retrieved using the GoodReads API (total GoodReads reviews, average rating)

Users can leave a review (one per user per book) which then displays on the book detail page. Users can also access their review history.

File Directory:

Server Files:

app.py:

  Main controller for the program, includes routes to create a new user, login an existing user, search for a book, retrieve details for a selected book, leave a review for a selected book, and access review history for a logged in user.

  App.py is connected to three postgresQL table (one that stores user/password info, one that stores book information, and one that stores review information)

  The book and review tables are mutually accessible as ISBN is a foreign key.

helpers.py:

  Contains the login required decorator function to ensure that certain routes in app.py are only accessible to logged in users.

import.py

  This file does not figure into the server code but is a project required auxiliary file that was used to import the books from the provided books.csv file into the books SQL data table. It uses the DictReader method from the python CSV module to convert the data in the csv file to an iterable list, and then iterates over these rows, creating a new row in the SQL table each time with the book information (title, ISBN, author, year of publication)

Web Templates:

login.html and register.html:

  Allows users to create a new account or login into to an existing one. There is client side input verification to ensure that blank entries are not being submitted and minimum password requirement of length of 5 characters is being met.

index.html:

  Users are directed here once logged in - provides an image based menu with an option to search for books or check past reviews they've made.

search.html:

  Users can search for books using any portion of a books title, author or isbn. Results are displayed via a table that renders in the space below the search bar. The title of each book in the table is a link that directs the user to a details page

details.html:

  Displays title, author, ISBN, publication year, number of goodreads reviews, average good reads rating, as well as any user submitted reviews. If users click the leave review button a div displaying radio buttons numbered 1-5 as well as a text box appear, allowing users to submit a rating and text review for the book. If the review is submitted successfully the user is redirected to index.html and a success banner appears indicating successful Submission

reviews_summary.html:

  Displays all of a users submitted review. Each review appears as a html card, similar to the display on details.html, however above each review card is a link to go to the details of the reviewed book (link text displays as title of the book)
