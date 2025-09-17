from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
import uuid
import bcrypt

# Load environment variables
load_dotenv()

# Try to import MongoDB with error handling
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
    print("✅ MongoDB import successful!")
except ImportError as e:
    print(f"⚠️  MongoDB import failed: {e}")
    print("⚠️  MongoDB functionality will be disabled.")
    MongoClient = None
    MONGODB_AVAILABLE = False

from bson import ObjectId
from datetime import datetime, timezone
import re
import traceback
import torch
from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import base64

# Try to import chatbot service with error handling
try:
    from chatbot_service_new import AnimalDiseaseChatbot
    CHATBOT_AVAILABLE = True
    print("✅ Chatbot service import successful!")
except ImportError as e:
    print(f"⚠️  Chatbot service import failed: {e}")
    print("⚠️  Chatbot functionality will be disabled.")
    AnimalDiseaseChatbot = None
    CHATBOT_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://kunalsurade016_db_user:umcunBXqOZO3AUK3@animal1.rydpf7k.mongodb.net/gorakshaai?retryWrites=true&w=majority"

# Initialize MongoDB connection variables
client = None
db = None
users_collection = None
predictions_collection = None

def initialize_mongodb():
    """Initialize MongoDB connection with the correct credentials"""
    global client, db, users_collection, predictions_collection
    
    if not MONGODB_AVAILABLE:
        print("⚠️  MongoDB not available - skipping database initialization")
        return False
    
    print("🔄 Initializing MongoDB connection...")
    
    try:
        # Create MongoDB client with proper configuration
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=30000,  # 30 seconds
            connectTimeoutMS=20000,          # 20 seconds
            socketTimeoutMS=20000,           # 20 seconds
            maxPoolSize=50,
            retryWrites=True
        )
        
        # Test the connection by pinging the admin database
        client.admin.command('ping')
        print("✅ MongoDB ping successful!")
        
        # Initialize database and collections  
        db = client['gorakshaai']
        users_collection = db['users']
        predictions_collection = db['predictions']
        
        # Create indexes for better performance
        try:
            users_collection.create_index("email", unique=True)
            predictions_collection.create_index("user_id")
            predictions_collection.create_index("created_at")
            print("✅ Database indexes created successfully!")
        except Exception as idx_error:
            print(f"⚠️  Index creation warning: {str(idx_error)}")
        
        # Test collections access
        user_count = users_collection.count_documents({})
        print(f"✅ Users collection accessible. Current user count: {user_count}")
        
        print("✅ MongoDB connected successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        print("⚠️  Starting without database - authentication will not work")
        
        # Set globals to None on failure
        client = None
        db = None
        users_collection = None
        predictions_collection = None
        return False

# Initialize chatbot service
chatbot = None

def initialize_chatbot():
    """Initialize chatbot service with better error handling"""
    global chatbot
    
    try:
        if not CHATBOT_AVAILABLE:
            print("⚠️  Chatbot service not available - chatbot functionality will be disabled")
            return False
        
        # Get Gemini API key from environment
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            return False
            
        if gemini_api_key == 'your-gemini-api-key-here':
            print("❌ Please set a valid GEMINI_API_KEY in your .env file")
            return False
        
        print("🔄 Initializing chatbot service...")
        chatbot = AnimalDiseaseChatbot(gemini_api_key)
        print("✅ Chatbot service initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        print("⚠️  Chatbot functionality will be disabled")
        chatbot = None
        return False

def get_chatbot_status():
    """Check if chatbot is available"""
    if chatbot is None:
        return False, "Chatbot not initialized"
    return True, "Chatbot ready"

def get_db_status():
    """Check if database is connected and available"""
    try:
        if client is None or db is None:
            return False, "Database not initialized"
        
        # Test connection
        client.admin.command('ping')
        return True, "Database connected"
    except Exception as e:
        return False, f"Database error: {str(e)}"

# Initialize MongoDB and chatbot on startup
print("🚀 Starting GoRakshaAI application...")
db_connected = initialize_mongodb()
if db_connected:
    print("🎉 Database connection established!")
else:
    print("⚠️  Application starting without database connection")

chatbot_initialized = initialize_chatbot()
if chatbot_initialized:
    print("🤖 Chatbot service is ready!")
else:
    print("⚠️  Application starting without chatbot functionality")

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize YOLO models
models = {}
try:
    # Load cat disease detection model
    if os.path.exists('models/cat_disease_best.pt'):
        models['cat'] = YOLO('models/cat_disease_best.pt')
        print("✅ Cat disease model loaded successfully!")
    else:
        print("⚠️  Cat disease model not found at models/cat_disease_best.pt")
    
    # Load cow disease detection model  
    if os.path.exists('models/lumpy_disease_best.pt'):
        models['cow'] = YOLO('models/lumpy_disease_best.pt')
        print("✅ Cow disease model loaded successfully!")
    else:
        print("⚠️  Cow disease model not found at models/lumpy_disease_best.pt")
    
    # Load dog disease detection model
    if os.path.exists('models/dog_disease_best.pt'):
        models['dog'] = YOLO('models/dog_disease_best.pt')
        print("✅ Dog disease model loaded successfully!")
    else:
        print("⚠️  Dog disease model not found at models/dog_disease_best.pt")
        
except Exception as e:
    print(f"❌ Error loading YOLO models: {e}")
    models = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard after login"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # Check if database is available
    if users_collection is None or predictions_collection is None:
        # Still show dashboard but with limited functionality
        return render_template('dashboard.html', 
                             user={'name': session.get('user_name', 'User'), 
                                   'email': session.get('user_email', '')}, 
                             recent_predictions=[],
                             db_unavailable=True)
    
    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        session.clear()
        return redirect(url_for('login_page'))
    
    # Get user's recent predictions
    recent_predictions = list(predictions_collection.find(
        {'user_id': session['user_id']}
    ).sort('created_at', -1).limit(5))
    
    return render_template('dashboard.html', user=user, recent_predictions=recent_predictions)

@app.route('/auth/login', methods=['POST'])
def login():
    """Handle login form submission"""
    try:
        # Check if database is available
        is_connected, status_msg = get_db_status()
        if not is_connected:
            return jsonify({
                'success': False, 
                'message': f'Database connection unavailable: {status_msg}. Please try again later.'
            }), 503
            
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Find user by email
        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password(password, user['password']):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Update last login
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        # Set session
        session['user_id'] = str(user['_id'])
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        
        print(f"✅ User logged in successfully: {email}")
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'redirect': url_for('dashboard')
        })
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/auth/signup', methods=['POST'])
def signup():
    """Handle signup form submission"""
    try:
        print("🔍 Signup request received")  # Debug log
        
        # Check if database is available
        is_connected, status_msg = get_db_status()
        if not is_connected:
            print(f"❌ Database not available: {status_msg}")
            return jsonify({
                'success': False, 
                'message': f'Database connection unavailable: {status_msg}. Please try again later.'
            }), 503
            
        # Get data from request
        data = request.get_json() if request.is_json else request.form
        print(f"🔍 Request content type: {request.content_type}")  # Debug log
        print(f"🔍 Request is_json: {request.is_json}")  # Debug log
        print(f"🔍 Signup data received: {data}")  # Debug log
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        print(f"🔍 Parsed data - Name: {name}, Email: {email}, Password length: {len(password) if password else 0}")  # Debug log
        
        # Validation
        if not all([name, email, password, confirm_password]):
            print("❌ Missing required fields")  # Debug log
            missing_fields = []
            if not name: missing_fields.append('name')
            if not email: missing_fields.append('email')
            if not password: missing_fields.append('password')
            if not confirm_password: missing_fields.append('confirm_password')
            print(f"❌ Missing fields: {missing_fields}")
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if password != confirm_password:
            print("❌ Passwords don't match")  # Debug log
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        if not validate_email(email):
            print(f"❌ Invalid email: {email}")  # Debug log
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"❌ Password validation failed: {message}")  # Debug log
            return jsonify({'success': False, 'message': message}), 400
        
        # Check if user already exists
        print(f"🔍 Checking if user exists: {email}")  # Debug log
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            print(f"❌ User already exists: {email}")  # Debug log
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
        
        # Create new user
        print(f"📝 Creating new user: {email}")  # Debug log
        hashed_password = hash_password(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        
        print(f"💾 Inserting user data into MongoDB...")  # Debug log
        result = users_collection.insert_one(user_data)
        print(f"✅ User created with ID: {result.inserted_id}")  # Debug log
        
        # Set session
        session['user_id'] = str(result.inserted_id)
        session['user_name'] = name
        session['user_email'] = email
        
        print(f"✅ Session created for user: {name}")  # Debug log
        
        return jsonify({
            'success': True, 
            'message': 'Account created successfully',
            'redirect': url_for('dashboard')
        })
        
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")  # Debug log
        print(f"❌ Error type: {type(e).__name__}")  # Debug log
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({'success': False, 'message': 'An error occurred during signup'}), 500
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({'success': False, 'message': f'An error occurred during signup: {str(e)}'}), 500

@app.route('/test-db')
def test_db():
    """Test MongoDB connection and show database status"""
    try:
        # Check database status
        is_connected, status_msg = get_db_status()
        
        if not is_connected:
            return jsonify({
                'success': False,
                'message': f'Database not connected: {status_msg}',
                'connection_string': MONGODB_URI.replace('umcunBXqOZO3AUK3', '***'),  # Hide password
                'collections': None,
                'user_count': 0
            }), 500
        
        # Test collection access
        user_count = users_collection.count_documents({})
        prediction_count = predictions_collection.count_documents({})
        
        # List collections
        collections = db.list_collection_names()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'database_name': 'gorakshaai',
            'collections': collections,
            'user_count': user_count,
            'prediction_count': prediction_count,
            'connection_string': MONGODB_URI.replace('umcunBXqOZO3AUK3', '***')  # Hide password
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database test failed: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/auth/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """Handle disease prediction requests"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Please login to use disease prediction'}), 401
        
        # Get form data
        animal_type = request.form.get('animal_type')
        symptoms = json.loads(request.form.get('symptoms', '[]'))
        age = request.form.get('age')
        weight = request.form.get('weight')
        temperature = request.form.get('temperature')
        additional_info = request.form.get('additional_info', '')
        
        # Handle file upload
        uploaded_file = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                uploaded_file = unique_filename
        
        # Mock disease prediction logic (replace with actual AI model)
        prediction_result = mock_disease_prediction(
            animal_type, symptoms, age, weight, temperature, additional_info
        )
        
        # Save prediction to database
        prediction_data = {
            'user_id': session['user_id'],
            'animal_type': animal_type,
            'symptoms': symptoms,
            'age': age,
            'weight': weight,
            'temperature': temperature,
            'additional_info': additional_info,
            'uploaded_file': uploaded_file,
            'prediction': prediction_result,
            'created_at': datetime.utcnow()
        }
        predictions_collection.insert_one(prediction_data)
        
        return jsonify({
            'success': True,
            'prediction': prediction_result,
            'uploaded_file': uploaded_file
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def mock_disease_prediction(animal_type, symptoms, age, weight, temperature, additional_info):
    """
    Mock disease prediction function
    Replace this with your actual AI model prediction logic
    """
    # Disease database for different animals
    disease_database = {
        'cattle': {
            'diseases': ['Bovine Respiratory Disease', 'Mastitis', 'Foot and Mouth Disease', 'Bloat', 'Milk Fever'],
            'symptoms_map': {
                'fever': ['Bovine Respiratory Disease', 'Foot and Mouth Disease'],
                'coughing': ['Bovine Respiratory Disease'],
                'difficulty_breathing': ['Bovine Respiratory Disease', 'Bloat'],
                'lethargy': ['Mastitis', 'Milk Fever'],
                'loss_of_appetite': ['Bloat', 'Milk Fever']
            }
        },
        'pig': {
            'diseases': ['Swine Flu', 'Porcine Reproductive and Respiratory Syndrome', 'Salmonellosis', 'Pneumonia'],
            'symptoms_map': {
                'fever': ['Swine Flu', 'Pneumonia'],
                'coughing': ['Swine Flu', 'Pneumonia'],
                'diarrhea': ['Salmonellosis'],
                'lethargy': ['Swine Flu', 'Salmonellosis']
            }
        },
        'chicken': {
            'diseases': ['Avian Influenza', 'Newcastle Disease', 'Coccidiosis', 'Fowl Pox'],
            'symptoms_map': {
                'fever': ['Avian Influenza', 'Newcastle Disease'],
                'difficulty_breathing': ['Avian Influenza', 'Newcastle Disease'],
                'diarrhea': ['Coccidiosis'],
                'skin_lesions': ['Fowl Pox']
            }
        },
        'sheep': {
            'diseases': ['Scrapie', 'Foot Rot', 'Parasitic Infections', 'Pneumonia'],
            'symptoms_map': {
                'lameness': ['Foot Rot'],
                'lethargy': ['Parasitic Infections', 'Pneumonia'],
                'coughing': ['Pneumonia']
            }
        },
        'goat': {
            'diseases': ['Caprine Arthritis Encephalitis', 'Pneumonia', 'Internal Parasites', 'Ketosis'],
            'symptoms_map': {
                'coughing': ['Pneumonia'],
                'lethargy': ['Internal Parasites', 'Ketosis'],
                'loss_of_appetite': ['Ketosis']
            }
        },
        'horse': {
            'diseases': ['Equine Influenza', 'Colic', 'Laminitis', 'Strangles'],
            'symptoms_map': {
                'fever': ['Equine Influenza', 'Strangles'],
                'coughing': ['Equine Influenza', 'Strangles'],
                'lameness': ['Laminitis']
            }
        },
        'dog': {
            'diseases': ['Parvovirus', 'Distemper', 'Kennel Cough', 'Hip Dysplasia'],
            'symptoms_map': {
                'vomiting': ['Parvovirus'],
                'diarrhea': ['Parvovirus'],
                'coughing': ['Kennel Cough', 'Distemper'],
                'lameness': ['Hip Dysplasia']
            }
        },
        'cat': {
            'diseases': ['Feline Leukemia', 'Upper Respiratory Infection', 'Feline Distemper', 'Urinary Tract Infection'],
            'symptoms_map': {
                'discharge': ['Upper Respiratory Infection'],
                'lethargy': ['Feline Leukemia', 'Feline Distemper'],
                'vomiting': ['Feline Distemper']
            }
        }
    }
    
    # Get animal data
    animal_data = disease_database.get(animal_type, {
        'diseases': ['General Infection', 'Nutritional Deficiency', 'Stress-related Condition'],
        'symptoms_map': {}
    })
    
    # Calculate disease probabilities based on symptoms
    disease_scores = {}
    for disease in animal_data['diseases']:
        disease_scores[disease] = 0
    
    # Add scores for matching symptoms
    for symptom in symptoms:
        if symptom in animal_data['symptoms_map']:
            for disease in animal_data['symptoms_map'][symptom]:
                if disease in disease_scores:
                    disease_scores[disease] += 10
    
    # Add base probability for all diseases
    for disease in disease_scores:
        disease_scores[disease] += 20  # Base probability
    
    # Sort diseases by score
    sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get top prediction
    top_disease = sorted_diseases[0][0] if sorted_diseases else 'Unknown Condition'
    confidence = min(95, max(60, sorted_diseases[0][1] * 2)) if sorted_diseases else 70
    
    # Generate recommendations
    recommendations = [
        "Consult with a veterinarian immediately for proper diagnosis",
        "Monitor the animal's condition closely",
        "Ensure proper nutrition and hydration",
        "Keep the animal comfortable and reduce stress"
    ]
    
    if 'fever' in symptoms:
        recommendations.append("Monitor body temperature regularly")
    if 'diarrhea' in symptoms or 'vomiting' in symptoms:
        recommendations.append("Ensure adequate fluid intake to prevent dehydration")
    if 'difficulty_breathing' in symptoms:
        recommendations.append("Ensure good ventilation and avoid stress")
    
    # Add isolation recommendation for certain diseases
    contagious_diseases = ['Avian Influenza', 'Newcastle Disease', 'Swine Flu', 'Foot and Mouth Disease']
    if top_disease in contagious_diseases:
        recommendations.insert(1, "Isolate the animal to prevent disease spread")
    
    return {
        'disease': top_disease,
        'confidence': round(confidence, 1),
        'symptoms_analyzed': symptoms,
        'recommendations': recommendations,
        'severity': 'High' if confidence > 80 else 'Medium' if confidence > 60 else 'Low',
        'animal_type': animal_type
    }

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/disease_detection')
def disease_detection():
    """Disease detection main page - animal selection"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('disease_detection.html')

@app.route('/cat_detection')
def cat_detection():
    """Cat disease detection page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('cat_detection.html')

@app.route('/predict/cat', methods=['POST'])
def predict_cat():
    """Predict cat diseases using YOLOv8 model"""
    try:
        # Check if model is loaded
        if 'cat' not in models:
            return jsonify({
                'success': False,
                'error': 'Cat disease detection model is not available'
            })

        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            })

        if file and allowed_file(file.filename):
            # Read image
            image_bytes = file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Run prediction
            results = models['cat'](image)
            
            # Process results
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = result.names[class_id]
                    
                    predictions.append({
                        'class': class_name,
                        'confidence': confidence
                    })
            
            # Sort by confidence
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Check if highest confidence is below 60%
            if predictions and predictions[0]['confidence'] < 0.6:
                return jsonify({
                    'success': False,
                    'error': 'Image quality is too low or does not contain a proper cat image. Please upload a clearer image of a cat.',
                    'confidence': predictions[0]['confidence'] if predictions else 0.0
                })
            
            # If no predictions, add a default
            if not predictions:
                return jsonify({
                    'success': False,
                    'error': 'No cat detected in the image. Please upload a clear image of a cat.',
                    'confidence': 0.0
                })
            
            # Store prediction in database if available
            if predictions_collection is not None:
                try:
                    prediction_doc = {
                        'user_id': session.get('user_id'),
                        'username': session.get('user_name'),
                        'animal_type': 'cat',
                        'predictions': predictions,
                        'timestamp': datetime.now(timezone.utc),
                        'model_used': 'cat_disease_best.pt'
                    }
                    predictions_collection.insert_one(prediction_doc)
                except Exception as db_error:
                    print(f"Database error: {db_error}")
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'model_info': 'YOLOv8 Cat Disease Detection Model'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Supported formats: PNG, JPG, JPEG, WebP'
            })
            
    except Exception as e:
        print(f"Error in cat prediction: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        })

@app.route('/predict/cow', methods=['POST'])
def predict_cow():
    """Predict cow diseases using YOLOv8 model"""
    try:
        # Check if model is loaded
        if 'cow' not in models:
            return jsonify({
                'success': False,
                'error': 'Cow disease detection model is not available'
            })

        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            })

        if file and allowed_file(file.filename):
            # Read image
            image_bytes = file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Run prediction
            results = models['cow'](image)
            
            # Process results
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = result.names[class_id]
                    
                    predictions.append({
                        'class': class_name,
                        'confidence': confidence
                    })
            
            # Sort by confidence
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Check if highest confidence is below 60%
            if predictions and predictions[0]['confidence'] < 0.6:
                return jsonify({
                    'success': False,
                    'error': 'Image quality is too low or does not contain a proper cow image. Please upload a clearer image of a cow.',
                    'confidence': predictions[0]['confidence'] if predictions else 0.0
                })
            
            # If no predictions, add a default
            if not predictions:
                return jsonify({
                    'success': False,
                    'error': 'No cow detected in the image. Please upload a clear image of a cow.',
                    'confidence': 0.0
                })
            
            # Store prediction in database if available
            if predictions_collection is not None:
                try:
                    prediction_doc = {
                        'user_id': session.get('user_id'),
                        'username': session.get('user_name'),
                        'animal_type': 'cow',
                        'predictions': predictions,
                        'timestamp': datetime.now(timezone.utc),
                        'model_used': 'lumpy_disease_best.pt'
                    }
                    predictions_collection.insert_one(prediction_doc)
                except Exception as db_error:
                    print(f"Database error: {db_error}")
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'model_info': 'YOLOv8 Cow Disease Detection Model'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Supported formats: PNG, JPG, JPEG, WebP'
            })
            
    except Exception as e:
        print(f"Error in cow prediction: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        })

@app.route('/predict/dog', methods=['POST'])
def predict_dog():
    """Predict dog diseases using YOLOv8 model"""
    try:
        # Check if model is loaded
        if 'dog' not in models:
            return jsonify({
                'success': False,
                'error': 'Dog disease detection model is not available'
            })

        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            })

        if file and allowed_file(file.filename):
            # Read image
            image_bytes = file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Run prediction
            results = models['dog'](image)
            
            # Process results
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = result.names[class_id]
                    
                    predictions.append({
                        'class': class_name,
                        'confidence': confidence
                    })
            
            # Sort by confidence
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Check if highest confidence is below 60%
            if predictions and predictions[0]['confidence'] < 0.6:
                return jsonify({
                    'success': False,
                    'error': 'Image quality is too low or does not contain a proper dog image. Please upload a clearer image of a dog.',
                    'confidence': predictions[0]['confidence'] if predictions else 0.0
                })
            
            # If no predictions, add a default
            if not predictions:
                return jsonify({
                    'success': False,
                    'error': 'No dog detected in the image. Please upload a clear image of a dog.',
                    'confidence': 0.0
                })
            
            # Store prediction in database if available
            if predictions_collection is not None:
                try:
                    prediction_doc = {
                        'user_id': session.get('user_id'),
                        'username': session.get('user_name'),
                        'animal_type': 'dog',
                        'predictions': predictions,
                        'timestamp': datetime.now(timezone.utc),
                        'model_used': 'dog_disease_best.pt'
                    }
                    predictions_collection.insert_one(prediction_doc)
                except Exception as db_error:
                    print(f"Database error: {db_error}")
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'model_info': 'YOLOv8 Dog Disease Detection Model'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Supported formats: PNG, JPG, JPEG, WebP'
            })
            
    except Exception as e:
        print(f"Error in dog prediction: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        })

@app.route('/cow_detection')
def cow_detection():
    """Cow disease detection page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('cow_detection.html')

@app.route('/dog_detection')
def dog_detection():
    """Dog disease detection page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dog_detection.html')

# =================== CHATBOT ROUTES ===================

@app.route('/chatbot')
def chatbot_page():
    """Render the chatbot interface"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle text-based chat messages - optimized for speed"""
    # Check if chatbot is available
    is_available, status_message = get_chatbot_status()
    if not is_available:
        return jsonify({
            'success': False, 
            'error': f'Chatbot service unavailable: {status_message}',
            'fallback_response': """I'm currently unable to connect to the AI service. Here are some things you can try:

🔧 **For Technical Issues:**
- Refresh the page and try again
- Check your internet connection
- Contact support if the problem persists

🐄 **For Animal Health Questions:**
- Document symptoms with photos if possible
- Note the animal's behavior changes
- Contact your local veterinarian for urgent cases

🩺 **Common Animal Diseases to Watch For:**
- Fever, loss of appetite, unusual discharge
- Lameness, difficulty breathing
- Skin lesions, swelling

**Emergency:** Call your veterinarian immediately for serious symptoms!
"""
        })
    
    try:
        # Get JSON data with timeout
        import threading
        import time
        
        start_time = time.time()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'})
            
        message = data.get('message', '').strip()
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'})
        
        print(f"📝 Processing message: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Process the query with progress tracking
        response = chatbot.process_text_query(message, language)
        
        processing_time = time.time() - start_time
        print(f"⚡ Response generated in {processing_time:.2f} seconds")
        
        # Store conversation in database if available (async to not slow down response)
        if db is not None and 'user_id' in session:
            try:
                conversation_doc = {
                    'user_id': session['user_id'],
                    'message': message,
                    'response': response.get('response', ''),
                    'language': language,
                    'timestamp': datetime.now(timezone.utc),
                    'type': 'text',
                    'processing_time': processing_time
                }
                db.conversations.insert_one(conversation_doc)
            except Exception as db_error:
                print(f"Database error storing conversation: {db_error}")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Server error: {str(e)}',
            'fallback_response': 'I encountered an error processing your request. Please try again or contact support if the problem persists.'
        })

@app.route('/api/chat/upload', methods=['POST'])
def upload_for_analysis():
    """Handle file uploads for analysis - optimized for better error handling"""
    # Check if chatbot is available
    is_available, status_message = get_chatbot_status()
    if not is_available:
        return jsonify({
            'success': False, 
            'error': f'Chatbot service unavailable: {status_message}',
            'fallback_response': 'File analysis is currently unavailable. Please try again later or contact support.'
        })
    
    try:
        import time
        start_time = time.time()
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        question = request.form.get('question', '')
        language = request.form.get('language', 'en')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Check file type and validate
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        print(f"📁 Analyzing uploaded file: {filename} ({file_ext})")
        
        if file_ext in ['png', 'jpg', 'jpeg', 'webp']:
            # Process as image with better error handling
            try:
                response = chatbot.analyze_image(file, question, language)
            except Exception as img_error:
                print(f"Image analysis error: {img_error}")
                return jsonify({
                    'success': False, 
                    'error': f'Image analysis failed: {str(img_error)}',
                    'fallback_response': 'Unable to analyze the uploaded image. Please try with a different image or describe the symptoms in text.'
                })
                
        elif file_ext == 'pdf':
            # Process as PDF
            try:
                response = chatbot.process_pdf(file, question, language)
            except Exception as pdf_error:
                print(f"PDF analysis error: {pdf_error}")
                return jsonify({
                    'success': False, 
                    'error': f'PDF analysis failed: {str(pdf_error)}',
                    'fallback_response': 'Unable to analyze the uploaded PDF. Please try with a different file or describe the content in text.'
                })
        else:
            return jsonify({
                'success': False, 
                'error': f'Unsupported file format: {file_ext}',
                'fallback_response': 'Please upload PNG, JPG, JPEG, WEBP images or PDF files only.'
            })
        
        processing_time = time.time() - start_time
        print(f"⚡ File analysis completed in {processing_time:.2f} seconds")
        
        # Store conversation in database if available
        if db is not None and 'user_id' in session:
            try:
                conversation_doc = {
                    'user_id': session['user_id'],
                    'file_name': filename,
                    'file_type': file_ext,
                    'question': question,
                    'response': response.get('response', ''),
                    'language': language,
                    'timestamp': datetime.now(timezone.utc),
                    'type': 'file_analysis',
                    'processing_time': processing_time
                }
                db.conversations.insert_one(conversation_doc)
            except Exception as db_error:
                print(f"Database error storing conversation: {db_error}")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in upload endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Upload processing failed: {str(e)}',
            'fallback_response': 'File upload encountered an error. Please try again with a different file or contact support.'
        })

@app.route('/api/chat/languages', methods=['GET'])
def get_languages():
    """Get available languages for the chatbot"""
    try:
        # Check if chatbot is available
        is_available, status_message = get_chatbot_status()
        if not is_available:
            # Return basic language list even if chatbot is not available
            basic_languages = {
                'en': 'English',
                'hi': 'Hindi', 
                'mr': 'Marathi',
                'te': 'Telugu',
                'ta': 'Tamil'
            }
            return jsonify({'success': True, 'languages': basic_languages})
        
        languages_list = chatbot.get_supported_languages()
        # Convert list format to dict format for frontend compatibility
        languages_dict = {lang['code']: lang['name'] for lang in languages_list}
        return jsonify({'success': True, 'languages': languages_dict})
        
    except Exception as e:
        print(f"Error getting languages: {e}")
        # Return basic language list on error
        basic_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi'
        }
        return jsonify({'success': True, 'languages': basic_languages})
    if not chatbot:
        return jsonify({'success': False, 'error': 'Chatbot service not available'})
    
    try:
        languages = chatbot.get_available_languages()
        return jsonify({'success': True, 'languages': languages})
    except Exception as e:
        print(f"Error getting languages: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat/clear', methods=['POST'])
def clear_conversation():
    """Clear the conversation history"""
    # Check if chatbot is available
    is_available, status_message = get_chatbot_status()
    if not is_available:
        return jsonify({'success': False, 'error': f'Chatbot service unavailable: {status_message}'})
    
    try:
        response = chatbot.clear_conversation()
        return jsonify(response)
    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get conversation history"""
    # Check if chatbot is available
    is_available, status_message = get_chatbot_status()
    if not is_available:
        return jsonify({'success': False, 'error': f'Chatbot service unavailable: {status_message}'})
    
    try:
        response = chatbot.get_conversation_history()
        return jsonify(response)
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat/health', methods=['GET'])
def chatbot_health_check():
    """Check chatbot service health"""
    # Check if chatbot is available
    is_available, status_message = get_chatbot_status()
    if not is_available:
        return jsonify({
            'success': True,
            'healthy': False,
            'services': {
                'genai_available': False,
                'vision_available': False,
                'pdf_available': False,
                'translation_available': False,
                'image_processing_available': False
            },
            'message': status_message
        })
    
    try:
        response = chatbot.health_check()
        return jsonify(response)
    except Exception as e:
        print(f"Error checking chatbot health: {e}")
        return jsonify({'success': False, 'error': str(e)})
        response = chatbot.clear_conversation()
        return jsonify(response)
    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)