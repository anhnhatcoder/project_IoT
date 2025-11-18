from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import paho.mqtt.client as paho
from paho import mqtt
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # Thêm cors để tránh lỗi kết nối

# ===== Flask routes =====
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client đã kết nối tới Web Server")
    try:
        with open('json_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        emit('json_data', data)
    except Exception as e:
        print("Chưa có dữ liệu cũ:", e)

# --- THÊM: Nhận lệnh bật/tắt bơm từ Web và gửi sang MQTT ---
@socketio.on('control_pump')
def handle_pump_control(data):
    # data nhận được là "ON" hoặc "OFF"
    print(f"Nhận lệnh điều khiển bơm: {data}")
    # Gửi lệnh này tới ESP32 qua MQTT
    client.publish("actuators/pump/cmd", data) 
# -----------------------------------------------------------

# ===== MQTT setup =====
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("anhnhat", "Sn29022004@1")

def on_connect(client, userdata, flags, rc, properties=None):
    print("Đã kết nối MQTT thành công!")
    client.subscribe("test/esp", qos=1)
    # Subscribe thêm topic trạng thái bơm để cập nhật lên web
    client.subscribe("actuators/pump/state", qos=0) 

client.on_connect = on_connect

def on_message(client, userdata, message):
    try:
        topic = message.topic
        payload = message.payload.decode("utf-8")
        
        # Xử lý dữ liệu cảm biến
        if topic == "test/esp":
            data = json.loads(payload)
            # Lưu file
            with open("json_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print("Cảm biến:", data)
            socketio.emit('json_data', data)
            
        # Xử lý trạng thái bơm (ESP báo về)
        elif topic == "actuators/pump/state":
            print("Trạng thái bơm:", payload)
            socketio.emit('pump_state', payload)

    except Exception as e:
        print("Lỗi xử lý dữ liệu:", e)

client.on_message = on_message
client.connect("403d6fe3f0414524a85849d2b0f71083.s1.eu.hivemq.cloud", 8883)

if __name__ == '__main__':
    client.loop_start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    #username: anhnhat
    #password: Sn29022004@1