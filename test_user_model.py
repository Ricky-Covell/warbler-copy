"""User model tests."""
#    FLASK_ENV=production python -m unittest<test_user_model.py>
#    python3 -m unittest test_user_model.py
import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Tests Message Class Functionality."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        
        db.session.rollback( )

    def test_user_model(self):
        """Does basic user model work?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u2.messages), 0)
        self.assertEqual(len(u2.followers), 0)



    def test_user_repr(self):
        """Does __repr__ work?"""

        u1 = User(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD")
        
        db.session.add(u1)
        db.session.commit()

        # User.__repr__ should be formatted correctly
        self.assertEqual(repr(u1), f'<User #{u1.id}: testuser1, test1@test.com>')



    def test_is_following(self):
        '''Does is_following & is_followed_by work?'''

        u1 = User(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD")
        u2 = User(email="test2@test.com", username="testuser2", password="HASHED_PASSWORD")

        u1.following.append(u2)

        db.session.add_all([u1, u2])
        db.session.commit()

        # u1 is following user u2 // u2 is being followed by u1
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))

        # u2 is not following user u1 // # u1 is not being followed by u2
        self.assertFalse(u2.is_following(u1))
        self.assertFalse(u1.is_followed_by(u2))

    
    def test_user_signup_and_authentication(self):
        '''Does user.create generate valid credentials?'''
        
        User.signup(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD", image_url='none')
        db.session.commit()

        # User is created
        self.assertTrue(len(User.query.all()) == 1) 

        # User credentials are authenticated or rejected correctly
        self.assertTrue(User.authenticate('testuser1', 'HASHED_PASSWORD'))
        self.assertFalse(User.authenticate('testuser1', 'wrong-password') )
        self.assertFalse(User.authenticate('wrong-username', 'HASHED_PASSWORD') )

        # User.authenticate returns user
        self.assertEqual(User.authenticate('testuser1', 'HASHED_PASSWORD'), User.query.filter_by(username='testuser1').one())


                    
        
        
