import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import timedelta
import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, paid_users
from config import config

class TestWebhookTransformer(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES

        # Clear paid_users set before each test
        paid_users.clear()

    def tearDown(self):
        pass

    def test_webhook_default(self):
        payload = {'message': 'Hello, world!'}
        response = self.app.post('/webhook', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_slack(self):
        payload = {'message': 'Hello, world!'}
        response = self.app.post('/webhook?format=slack', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_github_to_discord(self):
        payload = {
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "test/repo"
            },
            "pusher": {
                "name": "testuser"
            },
            "commits": [
                {},
                {}
            ]
        }
        response = self.app.post('/webhook?source=github&format=discord', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_invalid_source(self):
        payload = {'message': 'Hello, world!'}
        response = self.app.post('/webhook?source=invalid', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_webhook_stripe_to_msteams(self):
        payload = {
            "data": {
                "object": {
                    "amount": 1000,
                    "currency": "usd",
                    "billing_details": {
                        "email": "test@example.com"
                    }
                }
            }
        }
        response = self.app.post('/webhook?source=stripe&format=msteams', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_email_format(self):
        payload = {'subject': 'Test Email', 'body': 'This is a test email body.'}
        response = self.app.post('/webhook?format=email', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_invalid_format(self):
        payload = {'message': 'Hello, world!'}
        response = self.app.post('/webhook?format=invalid', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_webhook_shopify(self):
        payload = {
            "id": 1234567890,
            "email": "john.doe@example.com",
            "total_price": "50.00",
            "currency": "USD",
            "line_items": []
        }
        response = self.app.post('/webhook?source=shopify', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_wix(self):
        payload = {
            "orderNumber": "10002",
            "payments": [
                {
                    "amount": {
                        "value": "0.01",
                        "currency": "EUR"
                    }
                }
            ]
        }
        response = self.app.post('/webhook?source=wix', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_cloudflare(self):
        payload = {
            "name": "Test Webhook",
            "text": "A test event",
            "ts": 123456789,
            "data": {
                "notification_name": "Stream Live Input",
                "input_id": "eb222fcca08eeb1ae84c981ebe8aeeb6",
                "event_type": "live_input.disconnected",
                "updated_at": "2022-01-13T11:43:41.855717910Z"
            }
        }
        response = self.app.post('/webhook?source=cloudflare', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_webflow(self):
        payload = {
            "formId": "form123",
            "submissionId": "sub456",
            "data": {
                "email": "test@webflow.com",
                "name": "Webflow User"
            },
            "siteId": "site789",
            "triggeredBy": "form_submission",
            "triggeredAt": "2025-07-15T10:00:00.000Z"
        }
        response = self.app.post('/webhook?source=webflow', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @patch('requests_oauthlib.OAuth2Session')
    def test_discord_login_redirect(self, MockOAuth2Session):
        mock_discord_session = MockOAuth2Session.return_value
        mock_discord_session.authorization_url.return_value = (config.DISCORD_AUTHORIZATION_BASE_URL, "test_state")
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertIn(config.DISCORD_AUTHORIZATION_BASE_URL, response.headers['Location'])

    @patch('requests_oauthlib.OAuth2Session')
    @patch('app.add_user_to_discord_guild')
    def test_discord_callback_success(self, mock_add_user, MockOAuth2Session):
        mock_discord_session = MockOAuth2Session.return_value
        mock_discord_session.fetch_token.return_value = {"access_token": "discord_access_token"}
        mock_discord_session.get.return_value.json.return_value = {"id": "test_user_id", "username": "test_user"}

        response = self.app.get('/callback?code=test_code&state=test_state')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        mock_add_user.assert_called_once_with("test_user_id", "discord_access_token")

    def test_protected_access_unauthenticated(self):
        response = self.app.get('/protected')
        self.assertEqual(response.status_code, 401) # Unauthorized

    def test_protected_access_authenticated_unpaid(self):
        test_user_id = "unpaid_user"
        access_token = jwt.encode({"identity": test_user_id}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        response = self.app.get('/protected', headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 403) # Forbidden (not in paid_users)
        self.assertIn("Access denied. Please subscribe.", response.json['message'])

    def test_protected_access_authenticated_paid(self):
        test_user_id = "paid_user"
        paid_users.add(test_user_id) # Add user to paid_users
        access_token = jwt.encode({"identity": test_user_id}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        response = self.app.get('/protected', headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome, premium user!", response.json['message'])

    def test_refresh_token_success(self):
        test_user_id = "refresh_user"
        refresh_token = jwt.encode({"identity": test_user_id, "fresh": False}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        response = self.app.post('/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("access_token", data)

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_checkout_create):
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_stripe_checkout_create.return_value = mock_session

        test_user_id = "checkout_user"
        access_token = jwt.encode({"identity": test_user_id}, app.config['JWT_SECRET_KEY'], algorithm="HS256")

        response = self.app.post('/create-checkout-session', headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], "cs_test_123")
        mock_stripe_checkout_create.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_checkout_completed(self, mock_construct_event):
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': 'webhook_user_id',
                    'id': 'cs_test_webhook_id'
                }
            }
        }
        mock_construct_event.return_value = mock_event

        payload = json.dumps(mock_event)
        headers = {'stripe-signature': 'test_signature'}
        response = self.app.post('/webhook/stripe', data=payload, headers=headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('webhook_user_id', paid_users)

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "header")
        payload = "invalid_payload"
        headers = {'stripe-signature': 'invalid_signature'}
        response = self.app.post('/webhook/stripe', data=payload, headers=headers, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid signature", response.data.decode())

if __name__ == '__main__':
    unittest.main()
