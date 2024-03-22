import json
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        symbol = body.get("symbol")
        if not symbol:
            api_response = generate_response(400, {"msg": "Bad request. Missing symbol"})
            return api_response

        symbol = symbol.upper()

        logging.info(f"symbol is {symbol}")

        url = f"https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/diversification/sector/{symbol}"

        response: requests.Response = requests.get(url)

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        sector = data.get("db_result")

        if not sector:
            api_response = generate_response(500, {"msg": "No sector found"})
            return api_response

        url = f"https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/diversification/sector/complement/{sector}"

        response: requests.Response = requests.get(url)

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        sector_complement = data.get("db_result")

        if not sector:
            api_response = generate_response(500, {"msg": "No sector complement found"})
            return api_response

    #     get list of symbols in sector and return the 3 with the highest sharpe ratio
        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"SELECT symbol FROM spdr_sectors WHERE sector = %s;"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [sector_complement.upper()],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        sector_symbols = data.get("result")

        # now I have the list of symbols in sector. I need to get top 3 for sharpe ratio

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"SELECT * FROM sharpe_calc ORDER BY sharpe_ratio DESC;"

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        # todo need to get the symbol and sharpe ratio from db.

        symbols_desc = data.get("result")

        recommendations = search_sharpe_from_symbol(symbols_desc[:3], sector_symbols)

        api_response = generate_response(200, recommendations)

        return api_response



    except Exception as e:
        logging.error(f"Error: {e}")
        api_response = generate_response(500, {"msg": f"Error: {e}"})
        return api_response

def search_sharpe_from_symbol(search_symbols: list, all_symbols: list) -> list:
    result = []
    for search_symbol in search_symbols:
        for all_symbol in all_symbols:
            print(search_symbol[0].upper(), all_symbol.upper())
            if search_symbol[0].upper() == all_symbol.upper():
                result.append(search_symbol)
                break
    return result

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
