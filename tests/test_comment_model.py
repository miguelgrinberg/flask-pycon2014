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

    def test_markdown(self):
        c = Comment()
        c.body = '# title\n\n## section\n\ntext **bold** and *italic*'
        self.assertTrue(c.body_html == '<h1>title</h1>\n<h2>section</h2>\n'
                        '<p>text <strong>bold</strong> '
                        'and <em>italic</em></p>')

    def test_notification_list(self):
        db.create_all()
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='susan@example.com', username='susan', password='cat')
        t = Talk(title='t', description='d', author=u1)
        c1 = Comment(talk=t, body='c1', author_name='n1',
                     author_email='e@e.com', approved=True)
        c2 = Comment(talk=t, body='c2', author_name='n2',
                     author_email='e2@e2.com', approved=True, notify=False)
        c3 = Comment(talk=t, body='c3', author=u2, approved=True)
        c4 = Comment(talk=t, body='c4', author_name='n4',
                     author_email='e4@e4.com', approved=False)
        c5 = Comment(talk=t, body='c5', author=u2, approved=True)
        c6 = Comment(talk=t, body='c6', author_name='n6',
                     author_email='e6@e6.com', approved=True, notify=False)
        db.session.add_all([u1, u2, t, c1, c2, c3, c4, c5])
        db.session.commit()
        email_list = c4.notification_list()
        self.assertTrue(('e@e.com', 'n1') in email_list)
        self.assertFalse(('e2@e2.com', 'n2') in email_list)  # notify=False
        self.assertTrue(('susan@example.com', 'susan') in email_list)
        self.assertFalse(('e4@e4.com', 'n4') in email_list)  # comment author
        self.assertFalse(('e6@e6.com', 'n6') in email_list)
        email_list = c5.notification_list()
        self.assertFalse(('john@example.com', 'john') in email_list)
        self.assertTrue(('e4@e4.com', 'n4') in email_list)  # comment author
