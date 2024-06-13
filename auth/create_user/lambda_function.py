import json
import requests
import os
import bcrypt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        username: str = ""
        password: str = ""

        if "username" in body and "password" in body:
            username = body["username"]
            password = body["password"]
        else:
            formatted_response = generate_response(400, {"msg": "username and password required"})
            return formatted_response

        logging.info(f"username: {username} password: {password}")

        hashed_password = hash_password(password)
        str_password = hashed_password.decode('utf-8')

        logging.info("password hashed")

        # create user in account management tables
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"INSERT INTO app_users(username, password) VALUES (%s, %s);"
        query_params = (username, str_password)

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": query_params,
            "token": os.environ['TOKEN']
        })

        logging.info(f"response received {response}")

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return generate_response(500, {"msg": f"Error: code is {response.status_code}"})

        data = response.json()

        api_response = generate_response(200, data)

        return api_response

    except Exception as e:
        print(f"Error: {e}")
        return {"msg": f"Error: {e}"}


def hash_password(password: str):
    # Convert the password and phrase to bytes
    password = password.encode('utf-8')

    # Generate the salt using the phrase
    salt = bcrypt.gensalt(prefix=b"2b", rounds=12)

    # Hash the password using the salt
    hashed_password = bcrypt.hashpw(password, salt)

    return hashed_password


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
