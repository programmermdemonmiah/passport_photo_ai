from decimal import Decimal
from flask import Blueprint, jsonify, request

from db import get_db_connection

checkout_bp = Blueprint('checkout_bp', __name__)

@checkout_bp.route('/checkout', methods=['POST'])
def checkout():
    try:
        if request.headers['Content-Type'] != 'application/json':
            return jsonify({'Error': 'Unsupported Media Type. Please use Content-Type: application/json.'}), 415
        

        if not request.data.strip():
            return jsonify({'Error': 'name, phone, email, image_id, number_of_image, amount, delevery_address, payment_id and user_payment_id are required'}), 400

        
        data = request.get_json()
        
        
        required_fields = ['name', 'phone', 'email', 'image_id', 'number_of_image', 'amount', 'delevery_address', 'payment_id', 'user_payment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'Error': 'name, phone, email, image_id, number_of_image, amount, delevery_address, payment_id and user_payment_id are required'}), 400

        name = data['name']
        phone = data['phone']
        email = data['email']
        image_id = int(data['image_id'])
        number_of_image = int(data['number_of_image'])
        amount = Decimal(data['amount'])
        delevery_address = data['delevery_address']
        payment_id = data['payment_id']
        user_payment_id = data['user_payment_id']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            '''
            INSERT INTO checkout (name, phone, email, image_id, number_of_image, amount, delevery_address, payment_id, user_payment_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            ''',(name, phone, email, image_id, number_of_image, amount, delevery_address, payment_id, user_payment_id))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Order placed successfully.'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
