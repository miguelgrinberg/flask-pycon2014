import unittest
from app import create_app, db
from app.models import User, Talk, Comment, load_user


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        #db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_user_loader(self):
        db.create_all()
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(load_user(u.id) == u)

    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        with self.app.test_request_context('/',
                                           base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
        self.assertTrue('http://www.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar_ssl)

    def test_moderation(self):
        db.create_all()
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='susan@example.com', username='susan', password='cat',
                  is_admin=True)
        t = Talk(title='t', description='d', author=u1)
        c1 = Comment(talk=t, body='c1', author_name='n',
                     author_email='e@e.com', approved=True)
        c2 = Comment(talk=t, body='c2', author_name='n',
                     author_email='e@e.com', approved=False)
        db.session.add_all([u1, u2, t, c1, c2])
        db.session.commit()
        for_mod1 = u1.for_moderation().all()
        for_mod1_admin = u1.for_moderation(True).all()
        for_mod2 = u2.for_moderation().all()
        for_mod2_admin = u2.for_moderation(True).all()
        self.assertTrue(len(for_mod1) == 1)
        self.assertTrue(for_mod1[0] == c2)
        self.assertTrue(for_mod1_admin == for_mod1)
        self.assertTrue(len(for_mod2) == 0)
        self.assertTrue(len(for_mod2_admin) == 1)
        self.assertTrue(for_mod2_admin[0] == c2)
