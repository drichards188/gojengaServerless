import json

import mysql.connector
import os

from mysql.connector import errorcode

base_token = os.environ['TOKEN']


def lambda_handler(event, context):
    body = json.loads(event["body"])
    query = body["query"]
    user_token = body["token"]

    if user_token != base_token:
        return {
            'statusCode': 401,
            'body': "Token unauthorized"
        }

    print(f"query is {query}")

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

        stmt = f"{query}"
        cursor.execute(stmt)
        results = cursor.fetchall()

        if len(results) == 1:
            pretty_results = {}
            pretty_results["result"] = results[0]
        else:
            pretty_results = []
            for item in results:
                pretty_results.append(item[0])

        print(f"results are {pretty_results}")

        # Clean up
        cursor.close()
        connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps(pretty_results)
        }
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        print(f"Database connection failed: {err}")
        return {
            'statusCode': 500,
            'body': "Database connection failed"
        }
