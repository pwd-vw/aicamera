from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'aicamera_lpr'}

@app.route('/')
def index():
    return {'message': 'AI Camera Service Running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
