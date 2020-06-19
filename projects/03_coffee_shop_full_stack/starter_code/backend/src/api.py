import pprint
import sys
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, rollback
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN

db_drop_and_create_all()

## ROUTES

#there is no way for it to fail other than 500 afaik
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [d.short() for d in Drink.query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    drinks = [d.long() for d in Drink.query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    print('in post')
    data = request.get_json()
    pprint.pprint(data)
    title = data.get('title')
    recipe = data.get('recipe')
    #don't accept drink entries without all fields filled
    if not (title and recipe):
        abort(422)
    if not all(all(ingredient.values()) for ingredient in recipe):
        abort(422)
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    except Exception:
        rollback()
        print(sys.exc_info())
        abort(422)
    pprint.pprint(drink.long())

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200


@app.route('/drinks/<int:id_>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id_):
    print('in patch')
    print('id_', id_)
    drink = Drink.query.get(id_)
    if drink is None:
        abort(422)
    data = request.get_json()
    pprint.pprint(data)
    title = data.get('title')
    recipe = data.get('recipe')
    if title:
        drink.title = title
    if recipe:
        drink.recipe = json.dumps(recipe)
    try:
        drink.insert()
    except Exception:
        rollback()
        print(sys.exc_info())
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200


@app.route('/drinks/<int:id_>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id_):
    print('in delete')
    print('id_', id_)
    drink = Drink.query.get(id_)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        "delete": id_
    })


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(AuthError)
def autherror(ex):
    return jsonify(ex.error), ex.status_code
