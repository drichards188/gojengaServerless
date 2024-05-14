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

        url = "https://rjeu9nicn3.execute-api.us-east-2.amazonaws.com/dev/proxy"

        query = f"""SELECT spdr_calculations.corr_symbol, spdr_calculations.correlation, spdr_sectors.name FROM spdr_calculations JOIN spdr_sectors ON spdr_calculations.corr_symbol = spdr_sectors.symbol WHERE base_symbol = %s ORDER BY spdr_calculations.correlation ASC;"""

        response: requests.Response = requests.post(url, json={
            "query": query,
            "params": [symbol],
            "token": os.environ['TOKEN']
        })

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}")
            api_response = generate_response(500, {"msg": f"Error: {response.status_code}"})
            return api_response

        data = response.json()

        logging.info(f"data is {data}")

        symbols_desc = data.get("db_result")

        recommendations = symbols_desc[:3]
        map_recs = []
        for rec in recommendations:
            map_recs.append({"symbol": rec[0], "correlation": rec[1], "name": rec[2]})

        api_response = generate_response(200, {"result": map_recs})

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
