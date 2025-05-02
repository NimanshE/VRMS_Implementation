import unittest
from app import app, db, User
from werkzeug.security import check_password_hash

class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        # Set up the test client and database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        # Simulate user registration
        response = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'password123',
            'address': '123 Test Street',
            'phone': '1234567890'
        }, follow_redirects=True)

        # Check if the user was successfully registered
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            user = User.query.filter_by(email='testuser@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test User')
            self.assertTrue(check_password_hash(user.password, 'password123'))

if __name__ == '__main__':
    unittest.main()