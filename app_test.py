from flask import Flask
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return f"""
    <h1>Sistema Cámaras UFRO - Test Mínimo</h1>
    <p><strong>Status:</strong> ✅ Funcionando</p>
    <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
    <p><strong>Port:</strong> {os.environ.get('PORT', '8000')}</p>
    <p><strong>Python:</strong> {__version__}</p>
    """

@app.route('/env')
def env_check():
    return {
        'PORT': os.environ.get('PORT'),
        'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'NOT_SET',
        'DATABASE_URL': 'SET' if os.environ.get('DATABASE_URL') else 'NOT_SET'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)