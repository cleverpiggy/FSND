# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle GET requests for all available categories.
4. Create an endpoint to DELETE question using a question ID.
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
6. Create a POST endpoint to get questions based on category.
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422 and 500.

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API REFERENCE

### Endpoints

Method | URL | DATA
------ | ----| ----
GET    | /categories                   |
GET    | /questions?page={int}         |
DELETE | /questions/{int:id}           |
POST   | /questions/add                | REQUIRED
POST   | /questions/search             | REQUIRED
GET    | /categories/{int:id}/questions|
POST   | /quizzes                      | OPTIONAL


#### GET /categories
Returns a list of quiz categories and supplementary data as shown in the example.

Example:
```
$ curl http://127.0.0.1:5000/categories

{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true,
  "total_categories": 6
```
#### GET /questions?page={int}
Returns one page of questions and supplementary data as shown in the example.  Defaults to page one.

Example:
```
$ curl "http://127.0.0.1:5000/questions?page=2"
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Mona Lisa",
      "category": 2,
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    }, ...
  ],
  "success": true,
  "total_questions": 19
}
```
#### DELETE /questions/{int:id}
Deletes the question of the indicated id from the database.

Example:
```
$ curl -X DELETE http://127.0.0.1:5000/questions/17
{
  "question_id": 17,
  "success": true
}

```
#### POST /questions/add
Add a new question to the database.  Requires JSON with the following fields:

Key         | Value
---         | ---
'question'  | STRING
'answer'    | STRING
'category'  | INT
'difficulty'| INT

Example:
```
$ curl -X POST -H "Content-Type: application/json" \
-d '{"question": "Why?", "answer": "because", "category": 3, "difficulty": 2}' \
http://127.0.0.1:5000/questions/add
{
  "success": true
}

```

#### POST /questions/search
Returns a list of questions and supplementary data as shown in the example.  Required JSON contains a search string.  All questions are returned which contain that substring.

Key | Value
--- | ---
'searchTerm' | STRING

Example:
```
$curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"artist"}' http://127.0.0.1:5000/questions/search
{
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Jackson Pollock",
      "category": 2,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

#### GET /categories/{int:id}/questions
Returns all questions for the given category id and supplementary data as shown in the example.

Example:
```
$ curl http://127.0.0.1:5000/categories/2/questions
{
  "current_category": {
    "id": 2,
    "type": "Art"
  },
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "One",
      "category": 2,
      "difficulty": 4,
      "id": 18,
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    {
      "answer": "Jackson Pollock",
      "category": 2,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

#### POST /quizzes
Returns the next question in the game.  The question is chosen randomly and complies with optionally provided constraints:

Key | Value
--- | ---
'previous_questions' | int: LIST
'quiz_category'      | INT

Example:
```
% curl -X POST -H "Content-Type: application/json" \
-d '{"previous_questions": [19, 16], "quiz_category": 2}' \
http://127.0.0.1:5000/quizzes
{
  "question": {
    "answer": "One",
    "category": 2,
    "difficulty": 4,
    "id": 18,
    "question": "How many paintings did Van Gogh sell in his lifetime?"
  },
  "success": true
}

```

### Errors

Error codes 400, 404, 405, 422, and 500 all return the following format.

Example:

```
$ # improperly typed value for "category" \
curl -X POST -H "Content-Type: application/json" \
-d '{"question": "Why?", "answer": "because", "category": "three", "difficulty": 2}' \
http://127.0.0.1:5000/questions/add
{
  "error": 422,
  "message": "unprocessable",
  "success": false
}
```
