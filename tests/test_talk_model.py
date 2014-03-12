import unittest
from app import create_app, db
from app.models import User, Talk, Comment


class CommentModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        #db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_approved(self):
        db.create_all()
        u = User(email='john@example.com', username='john', password='cat')
        t = Talk(title='t', description='d', author=u)
        c1 = Comment(talk=t, body='c1', author_name='n',
                     author_email='e@e.com', approved=True)
        c2 = Comment(talk=t, body='c2', author_name='n',
                     author_email='e@e.com', approved=False)
        db.session.add_all([u, t, c1, c2])
        db.session.commit()
        approved = t.approved_comments().all()
        self.assertTrue(len(approved) == 1)
        self.assertTrue(approved[0] == c1)

    def test_unsubscribe(self):
        db.create_all()
        u = User(email='john@example.com', username='john', password='cat')
        t = Talk(title='t', description='d', author=u)
        c1 = Comment(talk=t, body='c1', author_name='n',
                     author_email='e@e.com', approved=True, notify=True)
        c2 = Comment(talk=t, body='c2', author_name='n',
                     author_email='e2@e2.com', approved=False, notify=True)
        c3 = Comment(talk=t, body='c3', author_name='n',
                     author_email='e@e.com', approved=False, notify=True)
        db.session.add_all([u, t, c1, c2, c3])
        db.session.commit()
        token = t.get_unsubscribe_token(u'e@e.com')
        Talk.unsubscribe_user(token)
        comments = t.comments.all()
        for comment in comments:
            if comment.author_email == 'e@e.com':
                self.assertTrue(comment.notify == False)
            else:
                self.assertTrue(comment.notify == True)

    def test_bad_unsubscribe_token(self):
        talk, email = Talk.unsubscribe_user('an invalid token')
        self.assertIsNone(talk)
        self.assertIsNone(email)
        u = User(email='john@example.com', username='john', password='cat')
        t = Talk(title='t', description='d', author=u)
        token = t.get_unsubscribe_token('e@e.com')
        talk, email = Talk.unsubscribe_user(token)
        self.assertIsNone(talk)
        self.assertIsNone(email)
