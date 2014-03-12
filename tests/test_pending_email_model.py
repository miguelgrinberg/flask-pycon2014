import unittest
from app import create_app, db
from app.models import PendingEmail, User, Talk


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

    def test_queue(self):
        db.create_all()
        u = User(email='john@example.com', username='john', password='cat')
        t1 = Talk(title='t1', description='d', author=u)
        t2 = Talk(title='t2', description='d', author=u)
        p = PendingEmail(name='n', email='e@e.com', subject='s',
                         body_text='t', body_html='h', talk=t1)
        db.session.add_all([u, t1, t2, p])
        db.session.commit()
        self.assertTrue(
            PendingEmail.already_in_queue('e@e.com', t1) == True)
        self.assertTrue(
            PendingEmail.already_in_queue('e2@e2.com', t1) == False)
        self.assertTrue(
            PendingEmail.already_in_queue('e@e.com', t2) == False)
