import json
import datetime
import bcrypt
import requests
import os
import jwt

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        username = body["username"]
        password = body["password"]

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        response: requests.Response = requests.post(url, json={
            "query": "SELECT username, password FROM users WHERE username='drichards';",
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return {"msg": "Error: {response['status_code']}"}

        data = response.json()

        db_password = data['result'][1]

        bytes_password = bytes(password, 'utf-8')
        bytes_db_password = bytes(db_password, 'utf-8')

        is_valid = bcrypt.checkpw(bytes_password, bytes_db_password)

        if (is_valid):
            return {
                'statusCode': 200,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                    "Access-Control-Allow-Methods": "*"
                },
                'body': json.dumps({
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    "token_type": "bearer"})
            }
        else:
            return {
                'statusCode': 401,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                    "Access-Control-Allow-Methods": "*"
                },
                'body': "Unauthorized"
            }

    except Exception as e:
        print(f"Error: {e}")
        return {"msg": f"Error: {e}"}


def hash_password(password: str, phrase: str):
    # Convert the password and phrase to bytes
    password = password.encode('utf-8')
    phrase = phrase.encode('utf-8')

    # Generate the salt using the phrase
    salt = bcrypt.gensalt(prefix=b"2b", rounds=12, salt=phrase)

    # Hash the password using the salt
    hashed_password = bcrypt.hashpw(password, salt)

    return hashed_password


def generate_access_token(user_id: str, secret_key: str):
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
