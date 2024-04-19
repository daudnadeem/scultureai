from datetime import datetime
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aws_lambda_powertools import Logger
from mangum import Mangum
import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from botocore.exceptions import ClientError

app = FastAPI()

logger = Logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dynamodb = boto3.resource("dynamodb")
table_name = "test_text_table"
table = dynamodb.Table(table_name)

cognito_client = boto3.client("cognito-idp")
def validate_user_id(event: APIGatewayProxyEvent):
    user_id = event.path_parameters.get("user_id")
    if user_id is None or not user_exists_in_cognito(user_id):
        raise HTTPException(status_code=401, detail="Unauthorized")

def user_exists_in_cognito(user_id: str) -> bool:
    try:
        response = cognito_client.list_users(
            UserPoolId=os.genviron.get("COGNITO_USER_POOL_ID")
        )
        user_ids = [user["Username"] for user in response["Users"]]
        return user_id in user_ids
    except ClientError as e:
        logger.exception("Error checking user existence in Cognito")
        return False

@app.post("/user/{user_id}/save")
def save_text(user_id: str, text: str):
    """Endpoint to save text for a specific user."""
    try:
        timestamp = datetime.now().isoformat()
        response = table.put_item(
            Item={
                "user_id": user_id,
                "text": text,
                "timestamp": timestamp
            }
        )
        return {"message": "Text saved successfully"}
    except Exception as e:
        logger.exception("Error saving text to DynamoDB")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/user/{user_id}/show")
def show_text(user_id: str):
    """Endpoint to show text for a specific user."""
    try:
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        items = response.get("Items", [])
        
        texts = []
        for item in items:
            if "text" in item and "timestamp" in item:
                texts.append({"text": item["text"], "timestamp": item["timestamp"]})
            else:
                logger.warning("Text or timestamp key is missing in DynamoDB item")
        
        return {"texts": texts}
    except Exception as e:
        logger.exception("Error retrieving texts from DynamoDB")
        raise HTTPException(status_code=500, detail="Internal Server Error")

handler = Mangum(app)