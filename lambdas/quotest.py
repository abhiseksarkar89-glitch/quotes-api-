import json
import random

def handler(event, context):

    quotes = [
        {
            "quote": "The greatest glory in living lies not in never falling, but in rising every time we fall.",
            "by": "Nelson Mandela"
        },
        {
            "quote": "The way to get started is to quit talking and begin doing.",
            "by": "Walt Disney"
        },
        {
            "quote": "Don't let yesterday take up too much of today.",
            "by": "Will Rogers"
        },
        {
            "quote": "The future belongs to those who believe in the beauty of their dreams.",
            "by": "Eleanor Roosevelt"
        },
        {
            "quote": "Tell me and I forget. Teach me and I remember. Involve me and I learn.",
            "by": "Benjamin Franklin"
        }
    ]

    # Get random quote
    item = random.choice(quotes)

    # Return API Gateway response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "Quote": "Hey Abhisek!"
        })
    }