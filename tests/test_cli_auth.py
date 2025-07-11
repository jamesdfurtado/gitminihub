import json
import time
from unittest.mock import patch, AsyncMock
from tests.test_helpers import AppTestCase
from app.api.cli_auth import auth_sessions, failed_logins, cleanup_expired_sessions
from datetime import datetime, timedelta, UTC


class CLIAuthTests(AppTestCase):

    def setUp(self):
        super().setUp()
        # Clear in-memory state
        auth_sessions.clear()
        failed_logins.clear()

    def test_auth_init_creates_token(self):
        """Test that /auth/init creates a CLI token."""
        resp = self.client.post("/auth/init")
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("cli_token", data)
        self.assertIn("login_url", data)
        self.assertTrue(data["cli_token"])
        self.assertIn(data["cli_token"], data["login_url"])

    def test_auth_init_returns_proper_url(self):
        """Test that login URL is properly formatted."""
        resp = self.client.post("/auth/init")
        data = resp.json()
        
        self.assertIn("http://testserver/cli-login?cli_token=", data["login_url"])
        self.assertIn(data["cli_token"], data["login_url"])

    def test_auth_init_creates_session(self):
        """Test that auth session is created in memory."""
        resp = self.client.post("/auth/init")
        data = resp.json()
        
        self.assertIn(data["cli_token"], auth_sessions)
        session = auth_sessions[data["cli_token"]]
        self.assertFalse(session["completed"])
        self.assertIsNone(session["username"])
        self.assertIsNone(session["raw_api_key"])

    def test_auth_verify_valid_credentials(self):
        """Test successful authentication with valid credentials."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Verify authentication
        resp = self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "testuser",
            "password": "testpass"
        })
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["message"], "Authentication successful")

    def test_auth_verify_invalid_token(self):
        """Test authentication with invalid CLI token."""
        self.create_user("testuser", password="testpass")
        
        resp = self.client.post("/auth/verify", json={
            "cli_token": "invalid-token",
            "username": "testuser",
            "password": "testpass"
        })
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid CLI token", resp.json()["detail"])

    def test_auth_verify_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Try with wrong password
        resp = self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "testuser",
            "password": "wrongpass"
        })
        
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Invalid credentials", resp.json()["detail"])

    def test_auth_verify_nonexistent_user(self):
        """Test authentication with non-existent user."""
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        resp = self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "nonexistent",
            "password": "testpass"
        })
        
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Invalid credentials", resp.json()["detail"])

    def test_auth_status_not_completed(self):
        """Test auth status when authentication not completed."""
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        resp = self.client.get(f"/auth/status?cli_token={cli_token}")
        
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Authentication not completed", resp.json()["detail"])

    def test_auth_status_completed(self):
        """Test auth status when authentication is completed."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Complete authentication
        self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "testuser",
            "password": "testpass"
        })
        
        # Check status
        resp = self.client.get(f"/auth/status?cli_token={cli_token}")
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["username"], "testuser")
        self.assertIn("api_key", data)
        self.assertTrue(data["api_key"])

    def test_auth_status_deletes_session(self):
        """Test that session is deleted after status check."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Complete authentication
        self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "testuser",
            "password": "testpass"
        })
        
        # Check status (should succeed)
        resp = self.client.get(f"/auth/status?cli_token={cli_token}")
        self.assertEqual(resp.status_code, 200)
        
        # Check status again (should fail - session deleted)
        resp2 = self.client.get(f"/auth/status?cli_token={cli_token}")
        self.assertEqual(resp2.status_code, 400)

    def test_api_key_stored_in_user_data(self):
        """Test that API key hash is stored in user data."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Complete authentication
        self.client.post("/auth/verify", json={
            "cli_token": cli_token,
            "username": "testuser",
            "password": "testpass"
        })
        
        # Check that API key was added to user data
        users = self.load_users()
        user_data = users["testuser"]
        self.assertIn("api_keys", user_data)
        self.assertEqual(len(user_data["api_keys"]), 1)
        self.assertTrue(user_data["api_keys"][0])

    def test_cli_login_page_loads(self):
        """Test that CLI login page loads with token."""
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        resp = self.client.get(f"/cli-login?cli_token={cli_token}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("GitMini CLI Authentication", resp.text)
        self.assertIn(cli_token, resp.text)

    def test_cli_login_page_missing_token(self):
        """Test CLI login page without token."""
        resp = self.client.get("/cli-login")
        self.assertEqual(resp.status_code, 400)

    def test_cli_login_existing_user(self):
        """Test CLI login with existing user."""
        self.create_user("testuser", password="testpass")
        
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Mock the API call
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"message": "Authentication successful"}
            
            resp = self.client.post("/cli-login", data={
                "cli_token": cli_token,
                "username": "testuser",
                "password": "testpass",
                "action": "login"
            }, follow_redirects=False)
            
            self.assertEqual(resp.status_code, 302)
            self.assertIn("/cli-success", resp.headers["location"])

    def test_cli_login_new_user(self):
        """Test CLI login with new user signup."""
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Mock the API call
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"message": "Authentication successful"}
            
            resp = self.client.post("/cli-login", data={
                "cli_token": cli_token,
                "username": "newuser",
                "password": "newpass",
                "action": "signup"
            }, follow_redirects=False)
            
            self.assertEqual(resp.status_code, 302)
            self.assertIn("/cli-success", resp.headers["location"])
            
            # Check that user was created
            users = self.load_users()
            self.assertIn("newuser", users)
            self.assertIn("api_keys", users["newuser"])

    def test_cli_success_page(self):
        """Test CLI success page."""
        resp = self.client.get("/cli-success?cli_token=test-token")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Authentication Successful", resp.text)

    def test_rate_limiting(self):
        """Test rate limiting for failed login attempts."""
        # Create CLI token
        init_resp = self.client.post("/auth/init")
        cli_token = init_resp.json()["cli_token"]
        
        # Make multiple failed attempts
        for i in range(6):
            resp = self.client.post("/auth/verify", json={
                "cli_token": cli_token,
                "username": "nonexistent",
                "password": "wrongpass"
            })
            
            if i < 5:
                self.assertEqual(resp.status_code, 401)
            else:
                # 6th attempt should be rate limited
                self.assertEqual(resp.status_code, 429)

    def test_session_cleanup(self):
        """Test that expired sessions are cleaned up."""
        # Create a session with past expiration
        cli_token = "test-token"
        auth_sessions[cli_token] = {
            "expires_at": datetime.now(UTC) - timedelta(minutes=1),
            "username": None,
            "raw_api_key": None,
            "completed": False
        }
        
        # Call init which should cleanup expired sessions
        resp = self.client.post("/auth/init")
        self.assertEqual(resp.status_code, 200)
        
        # Check that expired session was removed
        self.assertNotIn(cli_token, auth_sessions)

    def load_users(self):
        """Helper to load users from test file."""
        with open(self.users_path, "r") as f:
            return json.load(f) 