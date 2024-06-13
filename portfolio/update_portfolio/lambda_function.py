import json
import logging
import os
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    logging.info(f"event is {event}")

    body = json.loads(event["body"])

    username: str = ""
    quantity: int = 0
    asset: str = ""
    order_type: str = ""

    if "username" in body and "quantity" in body and "asset" in body and "order_type" in body:
        username = body["username"]
        quantity = body["quantity"]
        asset = body["asset"]
        order_type = body["order_type"]
    else:
        formatted_response = generate_response(400, {"msg": "username and password required"})
        return formatted_response

    try:
        url = f"https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/portfolio/{username}"

        response: requests.Response = requests.get(url)

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        current_quantity = 0
        portfolio = data.get("portfolio")
        for element in portfolio:
            if element.get("symbol") == asset:
                current_quantity = element.get("quantity")
                break

        if order_type == "sell":
            if current_quantity - quantity == 0:
                url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

                query = f"""DELETE p FROM portfolio p
                        JOIN app_users u ON p.user_id = u.id
                        JOIN assets a ON p.asset_id = a.id
                        WHERE u.username = %s AND a.name = %s;"""

                response: requests.Response = requests.post(url, json={
                    "query": query,
                    "params": [username, asset],
                    "token": os.environ['TOKEN']
                })

                if response.status_code != 200:
                    logging.error(f"Error: {response.status_code}")
                    api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
                    return api_response

                data = response.json()

                logging.info(f"data is {data}")

                api_response = generate_response(200, data)
                return api_response
            elif current_quantity >= quantity:
                current_quantity -= quantity
                if current_quantity < 0:
                    logging.error(f"Error: Not enough owned")
                    api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
                    return api_response

        elif order_type == "buy":
            current_quantity += quantity

        #     need to check if asset already owned or if buying for first time
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"""SELECT p.*
                FROM portfolio p
                JOIN app_users u ON p.user_id = u.id
                JOIN assets a ON p.asset_id = a.id
                WHERE u.username = %s AND a.name = %s;"""

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [username, asset],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        if data.get("db_result") == "No results found":
            url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

            query = f"""INSERT INTO portfolio (user_id, asset_id, quantity)
                    SELECT u.id, a.id, %s
                    FROM app_users u, assets a
                    WHERE u.username = %s AND a.name = %s;"""

            response: requests.Response = requests.post(url, json={
                "query": query,
                "params": [quantity, username, asset],
                "token": os.environ['TOKEN']
            })

            if response.status_code != 200:
                logging.error(f"Error: {response.status_code}")
                api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
                return api_response

            data = response.json()

            logging.info(f"data is {data}")

            api_response = generate_response(200, data)
            return api_response

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"""UPDATE portfolio p
                    JOIN assets a ON p.asset_id = a.id
                    SET p.quantity = %s
                    WHERE a.symbol = %s AND p.user_id = (
                        SELECT id
                        FROM app_users
                        WHERE username = %s
                    );"""

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [current_quantity, asset, username],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

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

def make_db_call(query: str, params: list) -> dict:
    url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

    response: requests.Response = requests.post(url, json={
        "query": query,
        "params": params,
        "token": os.environ['TOKEN']
    })

    if response.status_code != 200:
        logging.error(f"Error: {response.status_code}")
        api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
        return api_response

    data = response.json()

    logging.info(f"data is {data}")