import json
import logging
import mysql.connector
import os

import requests

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    symbol = event["pathParameters"]["symbol"]

    logging.info(f"symbol is {symbol}")


    try:
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"SELECT exchange FROM exchange_symbols WHERE symbol = %s;"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [symbol.upper()],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        api_response = generate_response(200, data["result"])

        return api_response
    except mysql.connector.Error as e:
        logging.error(f"Database connection failed: {e}")
        api_response = generate_response(500, {"msg": "Database connection failed"})
        return api_response


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
