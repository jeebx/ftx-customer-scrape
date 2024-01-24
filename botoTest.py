import os
import boto3
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

if not aws_key or not aws_secret or not aws_region:
    print("Missing AWS credentials. Please check your .env file.")
    exit(1)

try:
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=aws_region,
    )
    table = dynamodb.Table("ftx-customers")
except Exception as e:
    print(f"Failed to connect to AWS DynamoDB. Error: {e}")
    exit(1)


def get_dynamodb():
    return table
