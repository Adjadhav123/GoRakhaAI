#!/usr/bin/env python3
"""Simple script to test MongoDB connection"""

from pymongo import MongoClient
import sys

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://kunalsurade016_db_user:jc3YqkAHupwV6jk2@authentication.yykrupt.mongodb.net/gorakshaai?retryWrites=true&w=majority"

def test_connection():
    try:
        print("🔄 Attempting to connect to MongoDB Atlas...")
        
        # Simple connection
        client = MongoClient(MONGODB_URI)
        
        # Test the connection
        print("🔄 Testing connection with ping...")
        result = client.admin.command('ping')
        print(f"✅ Ping result: {result}")
        
        # Access database
        db = client['gorakshaai']
        print("✅ Database accessed successfully")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Collections: {collections}")
        
        # Test a simple operation
        users_collection = db['users']
        user_count = users_collection.count_documents({})
        print(f"👥 Current users in database: {user_count}")
        
        print("🎉 MongoDB connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)