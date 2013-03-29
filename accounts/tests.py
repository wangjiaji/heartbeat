from django.test import TestCase

class UserViewTests(TestCase):
    def test_login(self):
        response = self.client.post('/accounts/login/', {'username': 'test', 'password': 'z1x2c3'})
        self.assertEqual(response.status_code, 200)
