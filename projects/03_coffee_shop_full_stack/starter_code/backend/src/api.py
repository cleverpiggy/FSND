import pprint
import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, rollback
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#there is no way for it to fail other than 500 afaik
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [d.short() for d in Drink.query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    drinks = [d.long() for d in Drink.query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }) , 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    print ('in post')
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
    except:
        rollback()
        print(sys.exc_info())
        abort(422)
    pprint.pprint(drink.long())

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id_>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id_):
    print ('in patch')
    print ('id_', id_)
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
    except:
        rollback()
        print(sys.exc_info())
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id_>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id_):
    print ('in delete')
    print ('id_', id_)
    drink = Drink.query.get(id_)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        "delete": id_
    })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror(ex):
    return jsonify(ex.error), ex.status_code


# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpQRkxmZTVCY1lBS25YalBaeWkwdCJ9.eyJpc3MiOiJodHRwczovL2NsZXZlcnBpZ2d5LmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExNDU4OTE0MzY2MjI1MjIxNzE5MiIsImF1ZCI6WyJjb2ZmZWVzaG9wIiwiaHR0cHM6Ly9jbGV2ZXJwaWdneS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTkyNDMxMzIzLCJleHAiOjE1OTI0Mzg1MjMsImF6cCI6IkZWWXFpcUk4bTVkd3dHSUN6QnBDVHNPVHFTa3c0UVR0Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbXX0.FS6MQTznZPyDIeXuksGRUYno6cExpHLN4hec0VP5bgUW6HVpVL3zd3SGVyOUGJHFPJ1-i_PTOAvCme4rjw77stTltpKubZ5dSmXoZ6636Pokto7hETHKAl01zB0nXijOncznGFibBG6TmJuYzm_a5qajNQbsy58aoUQa573P0O61GIeaFsNZzaQbWo8JRoNEEMdQ-4V1OdhNQCDVmqOGU9-dORDQ6q2PrXs3RTZpPCJjfiPOrmjtycr7Ef3qbzbmLpavVw7gLzQMSo1zQRSZ4Ykem3zbQeNegUg29AqEcMJPIt9rpy9TUJPMCaKmxUdkZwUZju-zYCvt2cYSd-QY-g&scope=openid%20profile%20email&expires_in=7200&token_type=Bearer&state=g6Fo2SBMS3RJUGV2Qk1UVlNWSEtaZGFkV00xeTBvWEVIV3B3ZaN0aWTZIHpKYkNnZ2J2eDdSaFVPa2NyRnVaVUtGYVNqUld6R0hlo2NpZNkgRlZZcWlxSThtNWR3d0dJQ3pCcENUc09UcVNrdzRRVHQ
