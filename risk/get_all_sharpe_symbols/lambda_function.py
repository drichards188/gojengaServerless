import json
import requests
import mysql.connector
import os


def lambda_handler(event, context):
    try:
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        response: requests.Response = requests.post(url, json={
            "query": "SELECT exchange FROM exchange_symbols WHERE symbol = 'AAPL';",
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return {"msg": "Error: {response['status_code']}"}

        data = response.json()

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                "Access-Control-Allow-Methods": "*"
            },
            'body': json.dumps(data['result'])
        }

    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': "Database connection failed"
        }
