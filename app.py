import os
from flask import Flask, request, jsonify
from decimal import Decimal
import json
from dotenv import load_dotenv
from botoTest import get_dynamodb

table = get_dynamodb()

load_dotenv()

app = Flask(__name__)

env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


@app.route("/")
def hello():
    return "Found.xyz API for FTX customers"


@app.route("/get_customer_tokens", methods=["GET"])
def get_customer_tokens():
    # Get the customer ID from the query string parameter
    customer_id = request.args.get("customer_id")

    # Check if the customer ID was provided
    if not customer_id:
        return jsonify({"error": "Customer ID is required"}), 400

    try:
        # turn customer_id into num
        customer_id_num = int(customer_id)
        # Use the previously defined function to extract tokens
        tokens_json = table.get_item(Key={"customerId": customer_id_num})

        return tokens_json["Item"], 200
    except Exception as e:
        # Handle exceptions
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
