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
        
        self.user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        
        self.user3 = User.signup(username="testuser3",
                                    email="test@test3.com",
                                    password="testuser3",
                                    image_url=None)        
        db.session.commit()

    def test_search_empty(self):
        """Does empty search display every user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp.status_code, 200)

            # Search returns testuser & Users 2,3
            self.assertIn(f'<p>@{self.testuser.username }</p>', html)
            self.assertIn(f'<p>@{self.user2.username }</p>', html)
            self.assertIn(f'<p>@{self.user3.username }</p>', html)
  
            
    def test_search_for_user(self):
        """Does search for user display that user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            
            resp = c.get("/users?q=testuser2")
            html = resp.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp.status_code, 200)

            # Search returns User 2 // not testuser or User 3
            self.assertIn(f'<p>@{self.user2.username }</p>', html)
            self.assertNotIn(f'<p>@{self.testuser.username }</p>', html)
            self.assertNotIn(f'<p>@{self.user3.username }</p>', html)
            
            
    def test_profile_view(self):
        """Does profile display correctly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            
            resp = c.get(f"/users/{self.user2.id}")
            html = resp.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp.status_code, 200)

            # Search returns user2 bio & location
            self.assertIn(f'<p class="user-location"><span class="fa fa-map-marker"></span>{self.user2.location}</p>', html)        
            self.assertIn(f'<p>{self.user2.bio}</p>', html)        
     
            
    def test_following_view(self):
        """Does add follow work & does display correctly on followers page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.post(f'/users/follow/{self.user2.id}')
            
            # Make sure redirects
            self.assertEqual(resp1.status_code, 302)
            
            resp2 = c.get(f"/users/{self.testuser.id}/following")
            html = resp2.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp2.status_code, 200)

            # Search returns user2 is on testuser follow page
            self.assertIn(f'<p>@{self.user2.username}</p>', html)
            
    
    def test_followers_view(self):
        """Does add follow work & does display correctly on followers page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.post(f'/users/follow/{self.user2.id}')
            
            # Make sure redirects
            self.assertEqual(resp1.status_code, 302)
            
            resp2 = c.get(f"/users/{self.user2.id}/followers")
            html = resp2.get_data(as_text=True)

            # Make sure receive OK
            self.assertEqual(resp2.status_code, 200)

            # Shows testuser and notuser3 follows user2 
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)                
            self.assertNotIn(f'<p>@{self.user3.username}</p>', html)
            
    
    def test_likes(self):                
        """Do likes show up correctly?"""
            
        msg  = Message(
                text='testmessage',
                user_id= self.user2.id
            )
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:    
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.post(f'/users/handle_like/{msg.id}')

            # Make sure receive OK
            self.assertEqual(resp1.status_code, 302)

            resp2 = c.get(f'/users/{self.testuser.id}/likes')
            html = resp2.get_data(as_text=True)

            # Make sure ridirects
            self.assertEqual(resp2.status_code, 200)

            # Shows that testuser has liked user2 msg
            self.assertIn(f'<p>{ msg.text }</p>', html)