import json
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    try:
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        logging.info("Sending request")

        response: requests.Response = requests.post(url, json={
            "query": "SELECT symbol FROM sharpe_calc;",
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return {"msg": "Error: {response['status_code']}"}

        data = response.json()

        logging.info(f"data is {data}")

        api_response = generate_response(200, data)

        return api_response

    except Exception as e:
        logging.error(f"Error: {e}")
        api_response = generate_response(500, {"msg": f"Error: {e}"})
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
