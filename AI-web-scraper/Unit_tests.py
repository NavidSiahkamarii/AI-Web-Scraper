import unittest
from unittest.mock import patch, MagicMock
from user_management import insert_user, fetch_users, get_usernames, validate_username, log_in
from history import add_history, show_histories, fetch_histories
import json
import mysql
from SQL_Connection import get_connection

class TestUserFunctions(unittest.TestCase):

    @patch('SQL_Connection.get_connection')
    def test_insert_user(self, mock_get_connection):
        # Mocking database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        insert_user("testuser", "testpassword")

        # Assertions to ensure the SQL command was executed
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO accounts VALUES (%s, %s, %s, %s)",
            ("testuser", "testpassword", None, None)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('SQL_Connection.get_connection')
    def test_fetch_users(self, mock_get_connection):
        mock_cursor = MagicMock()
        mock_get_connection.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("user1", "pass1"), ("user2", "pass2")]

        users = fetch_users()

        # Check if the fetch_users function returns the expected result
        mock_cursor.execute.assert_called_once_with("SELECT * FROM accounts")
        self.assertEqual(users, [("user1", "pass1"), ("user2", "pass2")])

    @patch('SQL_Connection.get_connection')
    def test_get_usernames(self, mock_get_connection):
        mock_cursor = MagicMock()
        mock_get_connection.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("user1", ""), ("user2", "")]

        usernames = get_usernames()

        # Check the returned usernames
        mock_cursor.execute.assert_called_once_with("SELECT * FROM accounts")
        self.assertEqual(usernames, ["user1", "user2"])

    def test_validate_username(self):
        self.assertTrue(validate_username("validUser123"))
        self.assertFalse(validate_username("invalid user!"))
        self.assertFalse(validate_username(""))

    @patch('streamlit.st')
    @patch('user_management.fetch_users')
    def test_log_in_success(self, mock_fetch_users, mock_st):
        # Mocking the users returned from fetch_users
        mock_fetch_users.return_value = [{'username': 'user1', 'password': 'pass1'}]
        mock_st.session_state = {}

        # Simulating Streamlit input
        mock_st.text_input = MagicMock(side_effect=["user1", "pass1"])
        mock_st.form_submit_button = MagicMock(return_value=True)

        log_in()

        self.assertTrue(mock_st.session_state['logged_in'])
        self.assertEqual(mock_st.session_state['username'], "user1")

    @patch('streamlit.st')
    @patch('user_management.fetch_users')
    def test_log_in_fail(self, mock_fetch_users, mock_st):
        # Mocking the users returned from fetch_users
        mock_fetch_users.return_value = [{'username': 'user1', 'password': 'pass1'}]
        mock_st.session_state = {}

        # Simulating Streamlit input
        mock_st.text_input = MagicMock(side_effect=["user1", "wrongpass"])
        mock_st.form_submit_button = MagicMock(return_value=True)

        log_in()

        self.assertFalse('logged_in' in mock_st.session_state)


class TestHistoryFunctions(unittest.TestCase):

    @patch('SQL_Connection.get_connection')
    @patch('history.fetch_histories')
    def test_add_history(self, mock_fetch_histories, mock_get_connection):
        # Mocking the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mock return value for fetch_histories
        mock_fetch_histories.return_value = [("http://example.com", "Test Prompt", "Some Result")]

        username = "testuser"
        history_item = ("http://newurl.com", "New Prompt", "New Result")

        add_history(username, history_item)

        # Verify that fetch_histories was called
        mock_fetch_histories.assert_called_once_with(username)

        # Assert that the update command is correctly prepared
        updated_histories = [("http://example.com", "Test Prompt", "Some Result"), history_item]
        json_histories = json.dumps(updated_histories)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE accounts SET histories = %s WHERE username = %s",
            (json_histories, username)
        )
        mock_connection.commit.assert_called_once()

    @patch('main.st')
    def test_show_histories_no_histories(self, mock_st):
        show_histories([])

        # Verifying that the warning message is displayed
        mock_st.write.assert_called_once_with("No histories found")

    @patch('main.st')
    @patch('SQL_Connection.get_connection')
    def test_show_histories_with_data(self, mock_get_connection, mock_st):
        histories = [
            ("http://example.com", "Test Prompt", "Test Result")
        ]

        show_histories(histories)

        # Check that expander and content are displayed properly
        mock_st.expander.assert_called_once_with("Search: Test Prompt", expanded=False)
        mock_st.write.assert_any_call("**URL:** http://example.com")
        mock_st.write.assert_any_call("**Prompt:** Test Prompt")
        mock_st.text_area.assert_called_once_with("Test Result", key=mock_st.text_area.call_args[1]['key'], height=300)

    @patch('SQL_Connection.get_connection')
    def test_fetch_histories(self, mock_get_connection):
        mock_cursor = MagicMock()
        mock_get_connection.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (json.dumps([("http://example.com", "Test Prompt", "Some Result")]),)

        result = fetch_histories("testuser")

        # Verify that the expected SQL command was executed
        mock_cursor.execute.assert_called_once_with(
            "SELECT histories FROM accounts WHERE username = %s",
            ("testuser",)
        )

        # check if the result matches the expected output
        self.assertEqual(result, json.loads(mock_cursor.fetchone.return_value[0]))

class TestDatabaseConnection(unittest.TestCase):

    @patch('pymysql.connect')
    def test_get_connection(self, mock_connect):
        # Mock connection object
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Call the function to test
        connection = get_connection()

        # Ensure that pymysql.connect was called with the correct parameters
        mock_connect.assert_called_once_with(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=mysql.cursors.DictCursor,
            db="defaultdb",
            host="data-ai-web-scraper.d.aivencloud.com",
            password="AVNS_vXefrJYtYdAMfKfERON",
            read_timeout=10,
            port=10523,
            user="avnadmin",
            write_timeout=10,
        )

        # Ensure that the returned connection is the mocked connection
        self.assertEqual(connection, mock_connection)

if __name__ == '__main__':
    unittest.main()
