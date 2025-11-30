<<<<<<< HEAD
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OK", "message": "Aplicación funcionando correctamente"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "database": os.environ.get('DATABASE_URL', 'NOT_SET')})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
=======
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OK", "message": "Aplicación funcionando correctamente"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "database": os.environ.get('DATABASE_URL', 'NOT_SET')})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    app.run(host='0.0.0.0', port=port, debug=False)