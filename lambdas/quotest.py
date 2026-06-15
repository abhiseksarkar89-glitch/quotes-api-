import json
import boto3
import os
import uuid
import logging
from decimal import Decimal


# ✅ Configure Logging
logger = logging.getLogger()


# ✅ Read from environment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(log_level)


# ✅ CRITICAL FIX (this is why DEBUG was not working)
for handler in logger.handlers:
    handler.setLevel(log_level)



# ✅ DynamoDB Setup
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(os.environ["MY_TABLE"])


# ✅ Custom JSON Encoder (Decimal to float)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# ✅ Common Response Builder
def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }


# ✅ Lambda Handler
def handler(event, context):
    logger.info("Received request")
    logger.debug(f"Full event: {json.dumps(event)}")

    http_method = event.get("httpMethod")
    path_parameters = event.get("pathParameters") or {}
    quote_id = path_parameters.get("id")

    try:
        # ✅ CREATE QUOTE
        if http_method == "POST":
            logger.info("Processing POST request")

            body = json.loads(event.get("body") or "{}")
            logger.debug(f"Request body: {body}")

            quote = body.get("quote")
            by = body.get("by")

            if not quote or not by:
                logger.warning("Missing required fields: quote/by")

                return build_response(400, {
                    "success": False,
                    "message": "Both 'quote' and 'by' are required"
                })

            item = {
                "id": str(uuid.uuid4()),
                "quote": quote,
                "by": by
            }

            logger.debug(f"Generated item: {item}")

            table.put_item(Item=item)

            logger.info(f"Quote created successfully with id={item['id']}")

            return build_response(201, {
                "success": True,
                "message": "Quote created successfully",
                "data": item
            })


        # ✅ GET ALL QUOTES
        elif http_method == "GET" and not quote_id:
            logger.info("Processing GET request for all quotes")

            response = table.scan()
            items = response.get("Items", [])

            logger.debug(f"Fetched {len(items)} quotes")

            return build_response(200, {
                "success": True,
                "message": "Quotes fetched successfully",
                "data": items
            })


        # ✅ METHOD NOT ALLOWED
        else:
            logger.warning(f"Unsupported method: {http_method}")

            return build_response(405, {
                "success": False,
                "message": f"Method {http_method} not allowed"
            })

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

        return build_response(500, {
            "success": False,
            "message": "Internal server error"
        })