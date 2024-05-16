import json
import logging
import os
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    logging.info(f"event is {event}")
    username = event["pathParameters"]["username"]
    # username = "eric"
    logging.info(f"symbol is {username}")

    try:
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"""SELECT a.symbol, p.quantity
                    FROM assets a
                    JOIN portfolio p ON a.id = p.asset_id
                    WHERE p.user_id = (
                        SELECT id
                        FROM app_users
                        WHERE username = %s
                    );"""

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

        db_result = data.get("db_result")

        if db_result == "No results found":
            api_response = generate_response(200, {"portfolio": []})
            return api_response

        if len(db_result) % 2 == 0:
            portfolio = []
            coin_keys = []
            coin_quantities = []
            for coin in db_result:
                coin_keys.append(coin[0])
                coin_quantities.append(coin[1])

            for i in range(len(coin_keys)):
                portfolio.append({"symbol": coin_keys[i], "quantity": coin_quantities[i]})

        api_response = generate_response(200, {"portfolio": portfolio})

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
