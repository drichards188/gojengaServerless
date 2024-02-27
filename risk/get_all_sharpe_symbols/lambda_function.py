import json

import mysql.connector
import os


def lambda_handler(event, context):
    # Connection configuration
    config = {
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'raise_on_warnings': True
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        table_name = "spdr_calculations"

        stmt = f"SELECT symbol FROM {table_name};"
        cursor.execute(stmt)
        results = cursor.fetchall()
        pretty_results = []

        for item in results:
            pretty_results.append(item[0])

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
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': "Database connection failed"
        }
