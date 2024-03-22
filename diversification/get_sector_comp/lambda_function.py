import json
import logging
import os
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    logging.info(f"event is {event}")
    # sector = event["pathParameters"]["sector"]

    sector = "xlk"

    logging.info(f"symbol is {sector}")

    try:
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"SELECT match_name FROM index_matches WHERE index_name = %s;"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [sector.upper()],
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
