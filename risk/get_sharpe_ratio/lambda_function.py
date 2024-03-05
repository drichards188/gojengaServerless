import json
import logging

import mysql.connector
import os


def lambda_handler(event, context):
    if "pathParameters" in event:
        if "symbol" in event["pathParameters"]:
            symbol = event["pathParameters"]["symbol"]

    logging.info(f"symbol is {symbol}")

    # Connection configuration
    config = {
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'raise_on_warnings': True
    }

    # Connect to the database
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        table_name = "sharpe_calc"

        stmt = f"SELECT sharpe_ratio FROM {table_name} WHERE symbol = '{symbol.upper()}';"
        cursor.execute(stmt)
        results = cursor.fetchall()

        pretty_results = {}

        for item in results:
            pretty_results["sharpe_ratio"] = item[0]

        logging.info(f"pretty_results are {pretty_results}")

        # Clean up
        cursor.close()
        connection.close()

        api_response = generate_response(200, pretty_results)

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
