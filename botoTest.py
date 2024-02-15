import os
import boto3
from dotenv import load_dotenv

# Load .env file
load_dotenv()

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

if not aws_key or not aws_secret:
    print("Missing AWS credentials. Please check your .env file.")
    exit(1)

try:
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name="us-east-1",
    )
    table = dynamodb.Table("ftx-claims")
except Exception as e:
    print(f"Failed to connect to AWS DynamoDB. Error: {e}")
    exit(1)


def get_dynamodb():
    return table
