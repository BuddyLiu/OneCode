import ssl
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 设置一个目录来存储崩溃日志
UPLOAD_FOLDER = 'crash_logs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    # 返回一个简单的HTML页面作为主页
    return "Welcome to the Crash Log Uploader!"

@app.route('/upload_crash_log', methods=['POST'])
def upload_crash_log():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # 如果用户未上传文件，则返回错误
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    # 保存文件到指定目录
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 返回成功响应
    return jsonify({'message': 'Crash log uploaded successfully', 'filepath': filepath}), 200

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=context)
