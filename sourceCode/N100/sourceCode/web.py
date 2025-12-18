from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import json

app = Flask(__name__)

# ================= Global Variables =================
latest_data = {
    "timestamp": "-",
    "fps": 0,
    "objects": []
}

latest_frame = np.zeros((640, 640, 3), dtype=np.uint8)

# [추가] 현재 선택된 모델 (기본값: n_fp16)
current_target_model = "n_fp16"

# ================= Routes =================

@app.route('/')
def index():
    return render_template('index.html')

# [추가] 웹페이지에서 모델 변경 요청을 받는 API
@app.route('/set_model', methods=['POST'])
def set_model():
    global current_target_model
    try:
        req = request.json
        new_model = req.get('model')
        if new_model:
            current_target_model = new_model
            print(f"--> [명령] 모델 변경 요청됨: {new_model}")
            return jsonify({"status": "ok", "message": f"Changed to {new_model}"})
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "error"})

@app.route('/receive_data', methods=['POST'])
def receive_data():
    """젯슨으로부터 JSON 데이터를 받고, **변경할 모델 정보**를 응답으로 줌"""
    global latest_data
    try:
        data = request.json
        latest_data = data
        
        # [핵심] 응답에 'target_model'을 실어서 보냄
        return jsonify({
            "status": "ok", 
            "target_model": current_target_model 
        })
    except Exception as e:
        print(f"JSON Error: {e}")
        return jsonify({"status": "error"})

@app.route('/receive_image', methods=['POST'])
def receive_image():
    global latest_frame
    try:
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if frame is not None:
            latest_frame = frame
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error"})

@app.route('/data_feed')
def data_feed():
    # 웹페이지에도 현재 모델 정보를 같이 줌
    response_data = latest_data.copy()
    response_data['current_model'] = current_target_model
    return jsonify(response_data)

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is None: continue
        ret, buffer = cv2.imencode('.jpg', latest_frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("=== 웹 서버 시작 (http://0.0.0.0:5000) ===")
    app.run(host='0.0.0.0', port=5000, threaded=True)
