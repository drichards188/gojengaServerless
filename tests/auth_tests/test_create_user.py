import json
import unittest
from unittest.mock import patch, MagicMock

from auth.create_user import lambda_function


class TestLambdaHandler(unittest.TestCase):
    @patch('requests.post')
    @patch('os.environ')
    def test_lambda_handler(self, mock_os, mock_post):
        # Set up mock environment variables
        mock_os.__getitem__.side_effect = lambda x: 'mock_token'

        # Set up mock response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Query executed successfully"
        mock_post.return_value = mock_response

        # Set up event for lambda_handler
        event = {
            "body": json.dumps({
                "username": "test_user",
                "password": "test_password"
            })
        }

        # Call lambda_handler
        response = lambda_function.lambda_handler(event, None)

        # Assert that requests.post was called with the correct arguments
        mock_post.assert_called_once_with(
            "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy",
            json={
                "query": "INSERT INTO app_users(username, password) VALUES (%s, %s);",
                "params": ("test_user", "test_password"),
                "token": 'mock_token'
            }
        )

        # Assert that the response is correct
        self.assertEqual(response, {
            'statusCode': 200,
            'body': json.dumps({"result": "User created"})
        })

if __name__ == '__main__':
    unittest.main()