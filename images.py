from flask import Flask, Blueprint, jsonify
import os
from flask_cors import CORS
from imagebgremove import PROCESSED_IMAGES_DIR, UPLOADED_IMAGES_DIR

images_bp = Blueprint('images_bp', __name__)
CORS(images_bp)  # Enable CORS for the blueprint


@images_bp.route('/images', methods=['GET'])
def get_images():
    try:
        images = []
        for filename in os.listdir(PROCESSED_IMAGES_DIR):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_url = f'/api/processed_images/{filename}'
                images.append({
                    'image_name': filename, 
                    'image_url': image_url
                    })
        # for faild_filename in os.listdir(UPLOADED_IMAGES_DIR):
        #     if faild_filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        #         faild_image_url = f'/api/uploaded_images/{faild_filename}'
        #         images.append({
        #             'image_name': faild_filename, 
        #             'faild_image_url': faild_image_url,
        #             })

        return jsonify(images)

    except Exception as e:
        print(f"Exception during fetching images: {e}")
        return jsonify({'error': 'Internal server error'}), 500