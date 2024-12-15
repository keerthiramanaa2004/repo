import serial
import pickle
import pymysql
from flask import Flask, jsonify, render_template


# Flask setup
app = Flask(__name__)

# Connect to Arduino
arduino_port = 'COM3'  # Adjust as necessary
baud_rate = 9600
arduino = serial.Serial(arduino_port, baud_rate)

# Load the ML model
with open('ml_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Connect to MySQL
dbm = pymysql.connect(
    host='localhost',
    user='root',
    password='SIH2024',  # Replace with your MySQL password
    database='sensor_data'
)

# Create table if not exists
with dbm.cursor() as cursor:
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
    ''') #humidity FLOAT,
dbm.commit()



# Function to process data
def process_data(data):
    ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet = map(float, data.split(','))
    # Use the ML model for prediction
    input_features = [[ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet]]
    prediction = model.predict(input_features)[0]
 

    arduino.write(f"{prediction}\n".encode())  # Send value as a string with newline


    # Insert into MySQL database
    with dbm.cursor() as cursor:
        cursor.execute('''
            INSERT INTO processed_data (ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, ml_prediction)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, prediction))
    dbm.commit()

    return {
        'ppm_inlet': ppm_inlet,
        'co2_inlet': co2_inlet,
        'temp_inlet': temp_inlet,
        'ppm_outlet': ppm_outlet,
        'co2_outlet': co2_outlet,
        'ml_prediction': prediction
    }
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    if arduino.in_waiting > 0:
        raw_data = arduino.readline().decode('utf-8').strip()
        processed = process_data(raw_data)
        return jsonify(processed)
    return jsonify({'error': 'No data available'})


'''
@app.route('/data', methods=['GET'])
def fetch_data():
    try:
        # Connect to the database
        db = pymysql.connect(host='localhost', user='root', password='SIH2024', database='senser_data')
        cursor = db.cursor()
        
        # Query to fetch data
        query = "SELECT id, timestamp, ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, ml_prediction FROM processed_data"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Format data for JSON response
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})   
    finally:
        cursor.close()
        db.close()'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
