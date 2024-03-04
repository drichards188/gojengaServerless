import json
import requests
import os
import bcrypt


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        username = body["username"]
        password = body["password"]

        print(f"---> username: {username} password: {password}")

        hashed_password = hash_password(password)
        str_password = hashed_password.decode('utf-8')

        print("--> password hashed")

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"INSERT INTO app_users(username, password) VALUES ('{username}', '{str_password}');"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "token": os.environ['TOKEN']
        })

        print("--> response received")

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return {"msg": "Error: {response['status_code']}"}

        if response.text == "Query executed successfully":
            data = {"result": "User created"}
        else:
            data = response.json()

        print(f"--> data is {data}")

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                "Access-Control-Allow-Methods": "*"
            },
            'body': json.dumps(data['result'])
        }

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
