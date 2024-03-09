import json
import datetime
import bcrypt
import requests
import os
import jwt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        username = body["username"]
        password = body["password"]

        logging.info(f"username: {username} password: {password}")

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = "SELECT username, password FROM app_users WHERE username=%s;"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [username],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        db_password = data['result'][1]

        bytes_password = bytes(password, 'utf-8')
        bytes_db_password = bytes(db_password, 'utf-8')

        is_valid = bcrypt.checkpw(bytes_password, bytes_db_password)

        if is_valid:
            api_response = generate_response(200, {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer"})
            return api_response
        else:
            api_response = generate_response(401, {"msg": "Unauthorized"})
            return api_response

    except Exception as e:
        print(f"Error: {e}")
        return {"msg": f"Error: {e}"}



def generate_access_token(user_id: str, secret_key: str):
    try:
        # Define the expiration time for the token
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

        # Define the payload of the token
        payload = {
            'sub': user_id,  # subject of the token
            'iat': datetime.datetime.utcnow(),  # issued at
            'exp': expiration_time  # expiration time
        }

        # Encode the payload to generate the JWT
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token.decode('utf-8')
    except Exception as e:
        logging.error(f"Error generate_access_token: {e}")
        return None


def generate_response(status_code: int, body: dict, headers: dict = None) -> dict:
    if headers is None:
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
            "Access-Control-Allow-Methods": "*"
        }
    response = {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body)
    }
    return response
