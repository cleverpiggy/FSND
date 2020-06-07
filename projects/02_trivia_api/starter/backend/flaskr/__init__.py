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

  CORS(app)
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

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

