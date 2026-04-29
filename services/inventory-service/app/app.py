from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory inventory
inventory = {
    1: {'product_id': 1, 'quantity': 100},
    2: {'product_id': 2, 'quantity': 50},
    3: {'product_id': 3, 'quantity': 75}
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'inventory-service',
        'version': '1.0.0'
    })

@app.route('/api/v1/inventory/<int:product_id>', methods=['GET'])
def get_inventory(product_id):
    inv = inventory.get(product_id)
    if inv:
        return jsonify(inv)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/v1/inventory/<int:product_id>/reserve', methods=['POST'])
def reserve_inventory(product_id):
    data = request.json
    quantity = data.get('quantity', 1)
    
    if product_id in inventory:
        if inventory[product_id]['quantity'] >= quantity:
            inventory[product_id]['quantity'] -= quantity
            return jsonify({'status': 'reserved', 'remaining': inventory[product_id]['quantity']})
        return jsonify({'error': 'Insufficient stock'}), 400
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006, debug=True)
