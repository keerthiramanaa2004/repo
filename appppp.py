from flask import Flask, render_template, jsonify
import pymysql

app = Flask(__name__)

# MySQL database configuration
DB_HOST = "localhost"
DB_USER = "rooy"
DB_PASSWORD = "SIH2024"
DB_NAME = "sensor_data"
TABLE_NAME = "processed_data"

# Route to render the webpage
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/data', methods=['GET'])
def fetch_data():
    db = None  # Initialize the database connection
    cursor = None  # Initialize the cursor
    try:
        # Connect to the database
        db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = db.cursor()

        # Query to fetch data
        query = f"SELECT id, timestamp, ppm_inlet, co2_inlet, temp_inlet, ppm_outlet, co2_outlet, ml_prediction FROM {TABLE_NAME}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format data for JSON response
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        # Close cursor and connection if they were opened
        if cursor:
            cursor.close()
        if db:
            db.close()


if __name__ == '__main__':
    app.run(debug=True)
