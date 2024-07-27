import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app as app
from flask_cors import CORS
import os
from numpy import double
import rembg
from werkzeug.utils import secure_filename
from cropimage import detect_and_crop_face
from db import get_db_connection

# Define the blueprint
bg_remove_image_bp = Blueprint('bg_remove_image_bp', __name__)
CORS(bg_remove_image_bp)  # Enable CORS for the blueprint

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Background removal function
def remove_background(image_bytes):
    try:
        processed_bytes = rembg.remove(image_bytes)
        return processed_bytes  # Assuming processed_bytes is already in bytes format
    except Exception as e:
        print(f'Error removing background: {e}')
        raise


#db connection and insert and get data 
def db_insert_get_data(pathName):
    connection = get_db_connection()
    if connection:
        try:
            create_date = datetime.datetime.now()  # Current date and time
            expire_date = create_date + datetime.timedelta(days=30) 
            cursor = connection.cursor()
             # Insert the data
            cursor.execute(
                '''
                INSERT INTO photos (image, create_date, expire_date) VALUES (%s, %s, %s);
                ''', (pathName, create_date, expire_date)
            )

            # Fetch the inserted data
            cursor.execute(
                '''
                SELECT * FROM photos WHERE image = %s ORDER BY id DESC LIMIT 1;
                ''', (pathName,)
            )
            
            data = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()

            return data
            
        except Exception as e:
            print(f'DB Error excetion: {e}')
    else:
        print('error your db connection')


# Process and save image function
def process_and_save_image(file, heightPx, widthPx):
    try:
        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return jsonify({'error': 'Unsupported file format'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"File saved to {filepath}")  # Log file saved successfully

        # Read image bytes from saved file
        with open(filepath, 'rb') as f:
            image_bytes = f.read()
        listOfMessage = []
        face_cropped_bytes, original_image = detect_and_crop_face(image_bytes, heightPx, widthPx)

        if face_cropped_bytes:
            final_image_bytes = face_cropped_bytes
            listOfMessage.append("face detect successfully")
            listOfMessage.append("face crop successfully")
            # jsonify({'message': 'face detect successfully'})


        else:
            final_image_bytes = image_bytes
            listOfMessage.append("face detect unsuccessfully")
            listOfMessage.append("face crop unsuccessfully")
            return jsonify({'image': f'{filepath}', 'messages': listOfMessage}), 200

        processed_image_bytes = remove_background(final_image_bytes)
        if processed_image_bytes:
            listOfMessage.append("background remove successfully")
        else:
            listOfMessage.append("background remove unsuccessfully")
            return jsonify({'image': f'{filepath}', 'messages': listOfMessage}), 200


        processed_filename = secure_filename('processed_' + f'{datetime.datetime.now()}' + filename.split('.')[0] + '.png')
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)

        with open(processed_path, 'wb') as f:
            f.write(processed_image_bytes)

        print(f"Processed image saved to {processed_path}")  # Log processed image saved

        db_response = db_insert_get_data(f'{processed_path}')
        if db_response:
            return jsonify({'id': str(db_response[0]), 'image': str(db_response[1]), 'messages': listOfMessage})

        # return jsonify({'message': 'File processed successfully', 'image': f'{processed_path}'}) #'imagebyte': f'{list(processed_image_bytes)}'

    except Exception as e:
        print(f"Error processing file: {e}")  # Log detailed error message
        return jsonify({'error': str(e)}), 500

# Endpoint to handle image upload
@bg_remove_image_bp.route('/imageupload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        heightPx = request.form.get('height')
        widthPx = request.form.get('width')

        if not heightPx or not widthPx:
            return jsonify({'error': 'Please provide height and width in pixels'}), 400

        heightPx = int(double(heightPx))
        widthPx = int(double(widthPx))
        print(f"h:{heightPx}, w: {widthPx}")

        processed_response = process_and_save_image(file, heightPx, widthPx)
        if processed_response:
            return processed_response
        else:
            return jsonify({'message': 'Error processing file'}), 500

    except Exception as e:
        print(f"Exception during upload: {e}")
        return jsonify({'message': 'Internal server error'}), 500

PROCESSED_IMAGES_DIR = 'processed_images'

@bg_remove_image_bp.route('/processed_images/<filename>')
def send_image(filename):
    return send_from_directory(PROCESSED_IMAGES_DIR, filename)

UPLOADED_IMAGES_DIR = 'uploaded_images'
@bg_remove_image_bp.route('/uploaded_images/<filename>')
def serve_uploaded_image(filename):
    return send_from_directory(UPLOADED_IMAGES_DIR, filename)
