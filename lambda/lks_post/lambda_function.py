import json
import logging
import os

import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in body:
                return {
                    "statusCode": 400,
                    "body": json.dumps(f"Missing required field: {field}"),
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Content-Type": "application/json",
                    },
                }

        conn = pymysql.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            db=os.environ["DB_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    name, email, institution,
                    position, phone, image_url
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    body["name"],
                    body["email"],
                    body.get("institution"),
                    body.get("position"),
                    body.get("phone"),
                    body.get("image_url"),
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid

            cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
            user = cursor.fetchone()

        return {
            "statusCode": 201,
            "body": json.dumps(user, default=str),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json",
            },
        }

    except pymysql.IntegrityError as e:
        logger.error("Integrity error: %s", e)
        return {
            "statusCode": 409,
            "body": json.dumps("Email already exists"),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json",
            },
        }
    except pymysql.MySQLError as e:
        logger.error("Database error: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Database error: {str(e)}"),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json",
            },
        }
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}"),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json",
            },
        }
    finally:
        if "conn" in locals():
            conn.close()
