# Create your tests here.

import os
import unittest
import app

from datetime import date
from foundation_app.extensions import app, db, bcrypt
from foundation_app.models import Campaign, Donation, User

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_campaign():
    c1 = Campaign(
        name='first campaign',
        description='description goes here',
    )
    db.session.add(c1)

    c2 = Campaign(
        name='second campaign',
        description='another description goes here',
    )

    db.session.add(c2)
    db.session.commit()

def create_user():
    # Creates a user with username 'me1' and password of 'password'
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='moi', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(unittest.TestCase):

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    #TEST SIGNUP ROUTE
    def test_create_user(self):
        """Test creating a new user."""
        post_data = {
            'username': 'me1',
            'phone_number': '416-222-1234',
            'password': bcrypt.generate_password_hash('password').decode('utf-8'),
        }
        self.app.post('/signup', data=post_data)

        # Verify campaign was updated in the database
        new_user = User.query.filter_by(username='me1').first()
        self.assertEqual(new_user.phone_number, '416-222-1234')


    #TEST USER_ACCOUNT ROUTE
    
    def test_profile_page(self):
        create_user()
        login(self.app, 'moi', 'password')
        response = self.app.get('/user_account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # TODO: Verify that the response shows the appropriate user info
        response_text = response.get_data(as_text=True)
        self.assertIn('moi', response_text) 
        self.assertIn('Dashboard', response_text) 


    #TEST LOGGOUT ROUTE 

    def test_logout(self):
        """Test that Logout page shows appropriate msg."""
        # Set up
        create_user()
        login(self.app, 'moi', 'password')

        # Make a GET request
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('<p class="flash-message">Successfully logged out!</p>', response_text)
        self.assertIn('login', response_text)


