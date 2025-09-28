#!/usr/bin/env python
"""
Test script for room create API
"""

import json

# Simple test data with unique room number
import random
room_number = f"{random.randint(200, 999)}"

test_data = {
    "roomNo": room_number,
    "title": "Test Room",
    "roomDescription": "A test room for API testing",
    "category": "Standard", 
    "price_per_night": 2000.00,
    "beds": 1,
    "bathrooms": 1,
    "guests": 1,
    "television": True,
    "wifi": True,
    "air_condition": True
}

print("Test data for room creation:")
print(json.dumps(test_data, indent=2))
print("\nUse this data to test POST http://127.0.0.1:8000/api/rooms/create/")