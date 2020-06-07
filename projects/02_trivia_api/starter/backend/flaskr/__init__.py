import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randrange

from models import setup_db, Question, Category, rollback

QUESTIONS_PER_PAGE = 10


def select_random(query, randomrange=randrange):
  r = randomrange(0, query.count())
  return query.offset(r).first()


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    q = Category.query
    count = q.count()
    cats = {c.id: c.type for c in q}
    if count == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': cats,
      'total_categories': count
    })

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * QUESTIONS_PER_PAGE
    q1 = Question.query
    count = q1.count()
    if offset > count:
      abort(404)
    questions = q1.limit(QUESTIONS_PER_PAGE).offset(offset)
    cats = Category.query
    return jsonify({
      'success': True,
      'questions': [q.format() for q in questions],
      'total_questions': count,
      'categories': {c.id: c.type for c in cats}
    })

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  #DELETE /questions/${id}
  @app.route('/questions/<int:id_>', methods=['DELETE'])
  def delete_question(id_):
    question = Question.query.get(id_)
    if not question:
      abort(404)
    question.delete()

    return jsonify({
      'success': True,
      'question_id': id_
    })


  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  @app.route('/questions/add', methods=['POST'])
  def add_question():
    try:
      #insures the request had json with the appropriate keys/values
      fields = {
        'question': request.json['question'],
        'answer': request.json['answer'],
        'category': request.json['category'],
        'difficulty': request.json['difficulty']
      }
    except:
      abort(400)

    try:
      question = Question(**fields)
      question.insert()
    except:
      #should be due to inappropriate values for the database
      rollback()
      print(sys.exc_info())
      abort(422)

    return jsonify({
      'success': True
      })


  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    term = request.json.get('searchTerm')
    if term is None:
      abort(400)
    questions = Question.query.filter(Question.question .ilike(f'%{term}%'))

    return jsonify({
      'success': True,
      'total_questions': questions.count(),
      'questions': [q.format() for q in questions]
      })

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

  @app.route('/categories/<int:id_>/questions', methods=['GET'])
  def get_questions_by_category(id_):
    category = Category.query.get(id_)
    if not category:
      abort(404)
    questions = Question.query.filter_by(category=id_)

    return jsonify({
      'success': True,
      'total_questions': questions.count(),
      'questions': [q.format() for q in questions],
      'current_category': category.format()
      })

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  @app.route('/quizzes', methods=['POST'])
  def quiz():
    #i've decided there is no bad request.
    #They are getting a question whether they
    #like it or not.

    #list of ids
    prevs = request.json.get('previous_questions', [])
    cat_id = request.json.get('quiz_category')

    filters = [Question.id.notin_(prevs)]
    if cat_id:
      filters.append(Question.category == cat_id)
    query = Question.query.filter(*filters)

    question = None
    if query.count() > 0:
      question = select_random(query).format()

    #return result.question -- can be None
    return jsonify({
      'success': True,
      'question': question
      })

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'not found'
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'internal server error'
      }), 500

  return app

