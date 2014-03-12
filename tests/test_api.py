import unittest
import json
from app import create_app, db
from app.models import User, Talk, Comment


class CommentModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_token_errors(self):
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='susan@example.com', username='susan', password='cat')
        t = Talk(title='t', description='d', author=u1)
        c = Comment(talk=t, body='c1', author_name='n',
                    author_email='e@e.com', approved=False)
        db.session.add_all([u1, u2, t, c])
        db.session.commit()

        # missing JSON --> 400
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT'):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 400)

        # missing token --> 401
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'bad': 123}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 401)

        # bad token --> 401
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'token': 'a bad token'}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 401)

        # malformed token --> 401
        u3 = User(email='david@example.com', username='david', password='cat')
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'token': u3.get_api_token()}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 401)

    def test_approve(self):
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='susan@example.com', username='susan', password='cat')
        t = Talk(title='t', description='d', author=u1)
        c = Comment(talk=t, body='c1', author_name='n',
                    author_email='e@e.com', approved=False)
        db.session.add_all([u1, u2, t, c])
        db.session.commit()

        # wrong user --> 403
        token = u2.get_api_token()
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 403)

        # correct user --> 200
        token = u1.get_api_token()
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200)
            c = Comment.query.get(c.id)
            self.assertTrue(c.approved)

        # approve an already approved comment --> 400
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='PUT',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 400)

        # delete an already approved comment --> 400
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='DELETE',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 400)

    def test_delete(self):
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='susan@example.com', username='susan', password='cat')
        t = Talk(title='t', description='d', author=u1)
        c = Comment(talk=t, body='c1', author_name='n',
                    author_email='e@e.com', approved=False)
        db.session.add_all([u1, u2, t, c])
        db.session.commit()

        # wrong user --> 403
        token = u2.get_api_token()
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='DELETE',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 403)

        token = u1.get_api_token()
        with self.app.test_request_context(
                '/api/1.0/comments/' + str(c.id),
                method='DELETE',
                data=json.dumps({'token': token}),
                headers={'Content-Type': 'application/json'}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200)
            c = Comment.query.get(c.id)
            self.assertIsNone(c)
