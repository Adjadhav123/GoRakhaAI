
import ssl
from pymongo import MongoClient

print("Testing MongoDB connection...")
print(f"SSL Version: {ssl.OPENSSL_VERSION}")

# Test the corrected connection approach
MONGODB_URI = "mongodb+srv://kunalsurade016_db_user:umcunBXqOZO3AUK3@animal1.rydpf7k.mongodb.net/?retryWrites=true&w=majority&appName=animal1"

# Method 1: Try with explicit SSL context (Windows-friendly)
print("\n1. Testing connection with custom SSL context...")
try:
    # Create a more permissive SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')  # Lower security level for compatibility
    
    client = MongoClient(
        MONGODB_URI,
        ssl_context=ssl_context,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Connection successful with custom SSL context!")
    
    # Test database operations
    db = client['gorakshaai']
    print(f"✅ Database access successful!")
    print(f"Available collections: {db.list_collection_names()}")
    
    client.close()
    
except Exception as e:
    print(f"❌ Failed: {e}")

# Method 2: Try with standard TLS configuration
print("\n2. Testing connection with standard TLS...")
try:
    client = MongoClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Connection successful with standard TLS!")
    
    # Test database operations
    db = client['gorakshaai']
    print(f"✅ Database access successful!")
    print(f"Available collections: {db.list_collection_names()}")
    
    client.close()
    
except Exception as e:
    print(f"❌ Failed: {e}")

# Method 3: Try with certificate bypassing via connection string
print("\n3. Testing connection with connection string SSL options...")
try:
    # Add SSL options directly to connection string
    modified_uri = MONGODB_URI + "&ssl_cert_reqs=CERT_NONE&ssl_match_hostname=false"
    
    client = MongoClient(
        modified_uri,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Connection successful with connection string options!")
    
    # Test database operations
    db = client['gorakshaai']
    print(f"✅ Database access successful!")
    print(f"Available collections: {db.list_collection_names()}")
    
    client.close()
    
except Exception as e:
    print(f"❌ Failed: {e}")

print("\nConnection test completed.")