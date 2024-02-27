import json

import mysql.connector
import os


def lambda_handler(event, context):

    symbol = event["pathParameters"]["symbol"]

    print(f"symbol is {symbol}")

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

        print(f"results are {pretty_results}")

        # Clean up
        cursor.close()
        connection.close()

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                "Access-Control-Allow-Methods": "*"
            },
            'body': json.dumps(pretty_results)
        }
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, Is-Test',
                "Access-Control-Allow-Methods": "*"
            },
            'body': "Database connection failed"
        }
