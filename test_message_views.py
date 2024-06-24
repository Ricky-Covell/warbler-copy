import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY, do_logout

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_view_message(self):
        """Can view a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg  = Message(
                text='testmessage',
                user_id= self.testuser.id
            )
            db.session.add(msg)
            db.session.commit()
            
            resp = c.get(f"/messages/{msg.id}")
            html = resp.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp.status_code, 200)

            # Html response is correct
            self.assertIn(f'<p class="single-message">{ msg.text }</p>', html)
    
    
    def test_add_message(self):
        """Can use add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

                # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")



    def test_delete_message(self):
        '''Can user delete message?''' 
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
                
            msg = Message.query.one()
            
            resp = c.post(f"/messages/{msg.id}/delete")
            
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            
            # There should be no messages after msg is deleted
            self.assertEqual(len(Message.query.all()), 0)
        
        
    def test_logged_out_add(self):
        '''Is message add denied when user not logged in?'''
        
        c = self.client

        resp = c.post("/messages/new", data={"text": "Hello"})
        
        # Make sure it redirects
        self.assertEqual(resp.status_code, 302)
        
        # There should be no messages because user is unable to make post request
        self.assertEqual(len(Message.query.all()), 0)
        

    def test_delete_for_different_user(self):
        '''Can you delete different users message?'''
        
        u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        db.session.commit()
        
        msg_u2  = Message(
            text='testmessage u2',
            user_id= u2.id
        )
        db.session.add(msg_u2)
        db.session.commit() 
        
           
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        
            msg = Message.query.first()

            c.post(f"/messages/{msg.id}/delete")

            # There should be no messages after msg is deleted
            self.assertEqual(len(Message.query.all()), 1)
        
        
        