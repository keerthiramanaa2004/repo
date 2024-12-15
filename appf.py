import serial
import pickle
import pymysql
from flask import Flask, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Flask setup
appf = Flask(__name__)

# Connect to Arduino
arduino_port = 'COM3'  # Adjust as necessary
baud_rate = 9600
arduino = serial.Serial(arduino_port, baud_rate)

# Load the ML model
with open('ml_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Connect to MySQL
db_mysql = pymysql.connect(
    host='localhost',
    user='root',
    password='SIH2024',  # Replace with your MySQL password
    database='sensor_data'
)

# Create table if not exists
with db_mysql.cursor() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ppm_inlet INT,
            co2_inlet FLOAT,
            temp_inlet FLOAT,
            ppm_outlet INT,
            co2_outlet FLOAT,
            ml_prediction FLOAT
        )
    ''')
db_mysql.commit()

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')  # Replace with your JSON key file path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://zeolite-flow-prediction-default-rtdb.firebaseio.com/'  # Replace with your Firebase Realtime Database URL
})

# Firebase reference
firebase_ref = db.reference('processed_data')

# Function to process data
def process_data(data):
    ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet = map(float, data.split(','))
    # Use the ML model for prediction
    input_features = [[ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet]]
    prediction = model.predict(input_features)[0]

    arduino.write(f"{prediction}\n".encode())  # Send value as a string with newline

    # Insert into MySQL database
    with db_mysql.cursor() as cursor:
        cursor.execute('''
            INSERT INTO processed_data (ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, ml_prediction)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, prediction))
    db_mysql.commit()

    # Push to Firebase Realtime Database
    firebase_ref.push({
        'time_stamp': timestamp,
        'ppm_inlet': ppm_inlet,
        'co2_inlet': co2_inlet,
        'temp_inlet': temp_inlet,
        'ppm_outlet': ppm_outlet,
        'co2_outlet': co2_outlet,
        'ml_prediction': prediction
    })
    
    return {
        'ppm_inlet': ppm_inlet,
        'co2_inlet': co2_inlet,
        'temp_inlet': temp_inlet,
        'ppm_outlet': ppm_outlet,
        'co2_outlet': co2_outlet,
        'ml_prediction': prediction
    }

@appf.route('/')
def index():
    return render_template('index.html')

@appf.route('/data')
def get_data():
    if arduino.in_waiting > 0:
        raw_data = arduino.readline().decode('utf-8').strip()
        processed = process_data(raw_data)
        return jsonify(processed)
    return jsonify({'error': 'No data available'})

if __name__ == '__main__':
    appf.run(host='0.0.0.0', port=5000)
