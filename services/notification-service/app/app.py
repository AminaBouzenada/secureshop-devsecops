from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

notifications = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'notification-service',
        'version': '1.0.0'
    })

@app.route('/api/v1/notifications', methods=['POST'])
def send_notification():
    data = request.json
    notification = {
        'to': data.get('to'),
        'message': data.get('message'),
        'type': data.get('type', 'email'),
        'status': 'sent'
    }
    notifications.append(notification)
    print(f"Notification sent: {notification}")
    return jsonify(notification), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005, debug=True)
