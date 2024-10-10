import requests

from flask import Flask, request, jsonify
import pandas as pd
import uuid
import threading
import logging
from datetime import datetime

import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.my_sql_connection import MySQLConnection
from models.request import RequestModel
from models.product import ProductModel
from models.image import ImageModel

from utils.validate_csv_file import validate_csv

app = Flask(__name__)

# Initialize MySQL connection
db = MySQLConnection()

# Create tables if they do not exist
db.connect()  # Ensure the connection is established
db.create_tables()  # Create tables using the MySQLConnection class

request_model = RequestModel(db)
product_model = ProductModel(db)
image_model = ImageModel(db)


@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate CSV
        is_valid, validation_errors = validate_csv(file)
        if not is_valid:
            return jsonify({"error": "CSV validation failed", "details": validation_errors}), 400

        # Reset the file pointer after validation
        file.seek(0)

        # Read CSV file using pandas
        df = pd.read_csv(file)

        # Create a request record and get the request_id
        request_id = f'req_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
        request_model.create_request(request_id, 'started')

        # Prepare data for webhook
        webhook_data = {
            "request_id": request_id,
            "csv_data": df.to_dict(orient='records')
        }

        # Trigger the webhook for image processing
        webhook_url = "http://127.0.0.1:5000/webhook/image-processing"  # Replace with your webhook URL
        threading.Thread(target=trigger_webhook, args=(webhook_url, webhook_data)).start()

        return jsonify({"message": "CSV uploaded successfully", "request_id": request_id}), 201

    except Exception as e:
        logging.error(f"Error in upload_csv: {str(e)}")
        return jsonify({"error": str(e)}), 500


def trigger_webhook(webhook_url, data):
    try:
       response = requests.post(webhook_url, json=data)
       if response.status_code != 200:
           logging.error("Webhook processing failed")
           return jsonify({"error": "Image processing could not be initiated"}), 500
    except Exception as e:
        logging.error(f"Error in triggering webhook: {str(e)}")

def process_image(product_id, output_url):
    try:
        # Simulate image processing by updating image status and output URL
        image_model.update_status(product_id,output_url)
        # After processing, check for request completion
        check_request_completion(product_id)

    except Exception as e:
        logging.error(f"Error in image processing: {str(e)}")


def check_request_completion(product_id):
    try:
        # Find the request_id associated with the product
        request_id = product_model.get_request_id(product_id)[0][0]

        # Count total number of images and completed images for this request
        image_count = db.get("SELECT COUNT(*) FROM images WHERE product_id = %s", (product_id,))[0][0]
        completed_count = db.get("SELECT COUNT(*) FROM images WHERE product_id = %s AND status = %s", (product_id, 'completed'))[0][0]
        # If all images for the request are completed, update the request status to 'completed'
        if completed_count == image_count:
            request_model.update_request_status(request_id,'completed')

    except Exception as e:
        logging.error(f"Error in checking request completion: {str(e)}")


@app.route('/webhook/image-processing', methods=['POST'])
def image_processing_webhook():
    try:
        data = request.json
        request_id = data.get('request_id')
        csv_data = data.get('csv_data')

        if not request_id or not csv_data:
            return jsonify({"error": "Invalid data"}), 400

        # Process each product in the CSV data
        for row in csv_data:
            serial_number = row['sr.no']
            product_name = row['product name']
            input_url = row['image URL']

            # Generate UUIDs for products and images
            product_uuid = str(uuid.uuid4())  # Generate UUID for product
            image_uuid = str(uuid.uuid4())    # Generate UUID for image

            product_model.create_product(product_uuid, request_id, serial_number, product_name)
            image_model.create_image(image_uuid, product_uuid, input_url, 'processing')

            # Start image processing and get the output URL
            output_url = image_model.processing_image(input_url)

            # Process the image in the background
            process_image(product_uuid, output_url)

        return jsonify({"message": "Image processing initiated successfully"}), 200

    except Exception as e:
        logging.error(f"Error in image_processing_webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Endpoint to get request status by request_id
@app.route('/request/<string:request_id>', methods=['GET'])
def get_request_status(request_id):
    try:
        request_record = db.get('SELECT request_id, status, created_at, updated_at FROM requests WHERE request_id = %s', (request_id,))

        if request_record:
            return jsonify({
                "request_id": request_record[0][0],
                "status": request_record[0][1],
                "created_at": request_record[0][2],
                "updated_at": request_record[0][3]
            }), 200
        else:
            return jsonify({"error": "Request not found"}), 404

    except Exception as e:
        logging.error(f"Error in get_request_status: {str(e)}")
        return jsonify({"error": str(e)}), 500
