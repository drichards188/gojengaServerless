import json
import logging
import mysql.connector
import os

from mysql.connector import errorcode

base_token = os.environ['TOKEN']

# Set up logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    if "body" in event:
        body = json.loads(event["body"])

        if "query" in body and "token" in body:
            query = body["query"]
            client_token = body["token"]
        else:
            api_response = generate_response(400, {"msg": "Bad request. Missing reqs"})
            return api_response
    else:
        api_response = generate_response(400, {"msg": "Bad request. Missing body"})
        return api_response

    if "params" in body:
        params = body["params"]
    else:
        logging.critical("No params in body")

    if client_token != base_token:
        api_response = generate_response(401, {"msg": "Token unauthorized"})
        return api_response

    logging.info(f"query is {query}")

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

        query_verb = query.split(" ")[0].upper()

        if query_verb == 'INSERT' or query_verb == 'UPDATE' or query_verb == 'DELETE':
            # if insert query special execution function
            exec_response = execute_insert_query(connection, query, params)

            if exec_response:
                api_response = generate_response(200, {"msg": "Query executed successfully"})
                return api_response
        elif params == []:
            cursor = connection.cursor()

            cursor.execute(query)
            results = cursor.fetchall()
        else:
            cursor = connection.cursor()

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Clean up
            cursor.close()
            connection.close()

        if results == []:
            api_response = generate_response(200, {"db_result": "No results found"})
            return api_response

        if len(results) > 1:
            if results[0][1] != None and results[0][1] != "":
                pretty_results = []
                for item in results:
                    pretty_results.append(item)
                return generate_response(200, {"db_result": pretty_results})

            seperated_query = query.split(" ")
            raw_results = []
            if seperated_query[1] == "*":
                raw_results = []
                for item in results:
                    raw_results.append(item)
            else:
                for item in results:
                    raw_results.append(item[0])

            pretty_results = {}
            pretty_results["db_result"] = raw_results
            print(f"results are {results}")

        elif type(results[0]) == tuple and len(results[0]) > 1:
            raw_result = results[0]
            pretty_results = {}
            pretty_results["db_result"] = raw_result
        elif len(results[0]) == 1:
            pretty_results = {}
            pretty_results["db_result"] = results[0][0]
        else:
            raw_results = []
            print(f"results are {results}")
            for item in results:
                raw_results.append(item[0])

            pretty_results = {}
            pretty_results["db_result"] = raw_results

        logging.info(f"--> pretty_results are {pretty_results}")


        api_response = generate_response(200, {"result": pretty_results})
        return api_response

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        print(f"Database connection failed: {err}")
        api_response = generate_response(500, {"msg": f"Database connection failed: {err}"})
        return api_response


def execute_insert_query(connection, query, params):
    try:
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query, params)

        # Commit the transaction
        connection.commit()

        # Close the cursor
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


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
