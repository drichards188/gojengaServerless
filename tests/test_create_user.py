from unittest import TestCase

from auth.create_user.lambda_function import generate_response, hash_password


class Test(TestCase):
    def test_hash_password(self):
        hash = hash_password("password")
        self.assertIsNotNone(hash, "hash_password bad output")


    def test_generate_response(self):
        api_response = generate_response(200, {"msg": "Test run successfully"})
        self.assertEqual(api_response, {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                "Access-Control-Allow-Methods": "*"
            },
            'body': '{"msg": "Test run successfully"}'
        }, "generate_response bad output")
