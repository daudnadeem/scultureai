from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aws_lambda_powertools import Logger
from mangum import Mangum
import boto3
from boto3.dynamodb.conditions import Key

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

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

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