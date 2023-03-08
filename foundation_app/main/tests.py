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

class MainTests(unittest.TestCase):
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    # TEST CAMPAIGN ROUTE
    def test_create_campaign(self):
        """Test creating a campaign."""

        #Create a user & login
        create_user()
        login(self.app, 'moi', 'password')

        #POST request to the /new_campaign route
        post_data = {
            'name': 'third campaign',
            'description': 'A description for this',
        }
        self.app.post('/new_campaign', data=post_data)

        # Verify campaign was updated in the database
        created_campaign = Campaign.query.filter_by(name='third campaign').first()
        self.assertIsNotNone(created_campaign)
        self.assertEqual(created_campaign.name, 'third campaign')

    # TEST DONATE ROUTE
    def test_create_donation(self):
        """Test creating a donation."""

        #Create a user & login
        create_user()
        login(self.app, 'moi', 'password')
        create_campaign()

        #POST request to the /donation route
        post_data = {
            'amount': 100,
            'donated_by_id': 1,
            'donated_to': 1,
        }
        self.app.post('/donate', data=post_data)

        # Verify campaign was updated in the database
        donation = Donation.query.filter_by(amount='100').first()
        self.assertIsNotNone(donation)
        self.assertEqual(donation.amount, 100)


    # TEST HOMEPAGE ROUTE (WHEN NOT LOGGED IN)
    def test_homepage_logged_out(self):
            """Test that the book appears on its detail page."""

            response = self.app.get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            response_text = response.get_data(as_text=True)
            self.assertNotIn("Create a campaign", response_text)
            self.assertIn("Log in", response_text)

            