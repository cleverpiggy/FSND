import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from pprint import pprint

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        result = self.client().get('/categories')
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json["categories"])
        self.assertTrue(result.json["total_categories"])
        self.assertTrue(len(result.json["categories"]) > 0)

    def test_get_questions(self):
        result1 = self.client().get('/questions')
        result2 = self.client().get('/questions?page=2')
        for r in (result1, result2):
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json["questions"])
            self.assertTrue(r.json["total_questions"])
            self.assertTrue(len(r.json["questions"]) > 0)
        self.assertNotEqual(result1.json["questions"], result2.json["questions"])

    def test_get_question_from_page_out_of_range(self):
        result = self.client().get('/questions?page=1000')
        self.assertTrue(result.status_code, 404)

    def test_delete_question(self):
        q2 = Question.query.get(2)
        self.assertTrue(q2)
        result = self.client().delete('/questions/2')
        self.assertEqual(result.status_code, 200)
        q2 = Question.query.get(2)
        self.assertIsNone(q2)

    def test_delete_question_unused_id(self):
        nquestions = Question.query.count()
        result = self.client().delete('/questions/1000')
        nquestions2 = Question.query.count()
        self.assertTrue(result.status_code, 404)
        self.assertEqual(nquestions, nquestions2)

    def test_add_question(self):
        num_qs = Question.query.count()
        newq = {
            'question': 'Why',
            'answer': 'cuz',
            'category': 3,
            'difficulty': 3
        }
        result = self.client().post('/questions/add', json=newq)
        self.assertEqual(result.status_code, 200)
        q = Question.query.filter_by(**newq).one_or_none()
        self.assertIsNotNone(q)
        self.assertEqual(num_qs + 1, Question.query.count())

    def test_add_question_bad_values(self):
        num_qs = Question.query.count()
        newq = {
            'question': 'Why',
            'answer': 'cuz',
            'category': 'three',
            'difficulty': 4
        }
        result = self.client().post('/questions/add', json=newq)
        self.assertEqual(result.status_code, 422)
        self.assertFalse(result.json['success'])
        self.assertEqual(num_qs, Question.query.count())

    def test_add_question_bad_format(self):
        num_qs = Question.query.count()
        newq = {
            'age': 27,
            'race': 'purple',
            'favorite_food': 'taco',
            'difficulty': 4
        }
        result = self.client().post('/questions/add', json=newq)
        self.assertEqual(result.status_code, 400)
        self.assertFalse(result.json['success'])
        self.assertEqual(num_qs, Question.query.count())

        newq = 'I hate cheeze'
        result = self.client().post('/questions/add', json=newq)
        self.assertEqual(result.status_code, 400)
        self.assertFalse(result.json['success'])
        self.assertEqual(num_qs, Question.query.count())

    def test_search_question(self):
        search1 = {'searchTerm': 'alsdkj;'}
        search2 = {'searchTerm': 'the'}
        result1 = self.client().post('/questions/search', json=search1)
        result2 = self.client().post('/questions/search', json=search2)
        self.assertEqual(result1.status_code, 200)
        self.assertEqual(result1.json['total_questions'], 0)
        self.assertEqual(len(result1.json['questions']), 0)

        self.assertEqual(result2.status_code, 200)
        self.assertTrue(result2.json['total_questions'] > 0)
        self.assertTrue(len(result2.json['questions']) > 0)

    def test_get_question_by_category(self):
        #six categories
        category = 3
        result = self.client().get(f'/categories/{category}/questions')
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json['total_questions'] > 0)
        self.assertTrue(all(
            q['category'] == category
            for q in result.json['questions']
        ))
        self.assertEqual(result.json['current_category']['id'], category)

    def test_get_question_by_category_outofrange(self):
        #six categories
        category = 100
        result = self.client().get(f'/categories/{category}/questions')
        self.assertEqual(result.status_code, 404)

    def test_quiz(self, *, category_id=None):
        '''
        Continue to feed the endpoint keeping while track of previous
        questions until all questions have been returned.
        '''
        previous_questions = []
        json = {'previous_questions':previous_questions}
        if category_id:
            json['quiz_category'] = category_id
            q_query = Question.query.filter_by(category=category_id)
        else:
            q_query = Question.query
        while True:
            result = self.client().post('/quizzes', json=json)
            self.assertEqual(result.status_code, 200)
            question = result.json['question']
            #returned question will be None after all
            #possibilities are exhausted
            if not question:
                break
            self.assertNotIn(question['id'], previous_questions)
            previous_questions.append(question['id'])

        all_question_ids = {q.id for q in q_query}
        self.assertEqual(set(previous_questions), all_question_ids)

    def test_quiz_categories(self):
        for c in Category.query:
            self.test_quiz(category_id=c.id)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
