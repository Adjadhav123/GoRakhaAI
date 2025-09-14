from flask import Flask, render_template, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """Handle disease prediction requests"""
    try:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
