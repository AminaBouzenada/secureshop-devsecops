from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# In-memory orders storage
orders = []
order_id_counter = 1

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'order-service',
        'version': '1.0.0'
    })

@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    global order_id_counter
    data = request.json
    
    order = {
        'id': order_id_counter,
        'user_id': data.get('user_id'),
        'items': data.get('items', []),
        'total_amount': data.get('total_amount', 0),
        'status': 'pending'
    }
    
    orders.append(order)
    order_id_counter += 1
    
    return jsonify(order), 201

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True)
