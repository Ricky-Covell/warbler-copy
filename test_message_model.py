"""Message model tests."""
#    FLASK_ENV=production python3 -m unittest test_message_model.py
#    python3 -m unittest test_message_model.py
import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserMessageTestCase(TestCase):
    """Tests Message Class Functionality."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

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

        self.client = app.test_client()


    def tearDown(self):
        
        db.session.rollback( )



    def test_message_model(self):
        """Does basic message model work?"""
        user1 = User.query.filter(User.username == 'testuser1').first()
          
        m1 = Message(
            text='testmessage1',
            user_id= user1.id
        )

        db.session.add(m1)
        db.session.commit()

        # There should be 1 message in message class // user1 should have 1 message
        self.assertEqual(len(Message.query.all()), 1)
        self.assertEqual(len(user1.messages), 1)


    def test_delete_message(self):
        """Does message ondelete-cascade work?"""
        user1 = User.query.filter(User.username == 'testuser1').first()
          
        m1 = Message(
            text='testmessage1',
            user_id= user1.id
        )

        db.session.add(m1)
        db.session.commit()

        db.session.delete(m1)
        db.session.commit()
        
        # There should be 0 message in message class // user1 should have 0 messages
        self.assertEqual(len(Message.query.all()), 0)
        self.assertEqual(len(user1.messages), 0)