from flask import Flask
from imagebgremove import bg_remove_image_bp
import os
from images import images_bp
from checkout import checkout_bp

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploaded_images'
app.config['PROCESSED_FOLDER'] = 'processed_images'
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # Set to 16 MB (increase as needed)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)


@app.route('/')
def home():
    return "Hello, Welcome to Photo ai. made by programmermdemonmiah"

# Registering each blueprint under the '/api' prefix
app.register_blueprint(bg_remove_image_bp, url_prefix='/api')
app.register_blueprint(images_bp, url_prefix='/api')
app.register_blueprint(checkout_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
