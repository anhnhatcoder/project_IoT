import paho.mqtt.client as paho
from paho import mqtt
import json
import time

# --- CẤU HÌNH GIỐNG HỆT SERVER ---
BROKER_URL = "403d6fe3f0414524a85849d2b0f71083.s1.eu.hivemq.cloud"
PORT = 8883
USER = "anhnhat"
PASS = "Sn29022004@1"
TOPIC = "test/esp"

# Khởi tạo client
client = paho.Client(
    client_id="Python_Test_Sender", 
    protocol=paho.MQTTv5,
    callback_api_version=paho.CallbackAPIVersion.VERSION2
)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(USER, PASS)

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print("✅ Đã kết nối tới HiveMQ! Đang chuẩn bị gửi tin...")
        
        # Dữ liệu giả lập
        fake_data = {
            "temperature": 35.5,
            "humidity": 60,
            "rain": 1,
            "plant": {
                "name": "Cây Giả Lập",
                "status": "healthy",
                "soilMoist": 70,
                "leafTemp": 34
            }
        }
        
        # Chuyển thành chuỗi JSON
        payload = json.dumps(fake_data)
        
        # Gửi tin nhắn
        client.publish(TOPIC, payload)
        print(f"📤 Đã gửi: {payload}")
        
        # Ngắt kết nối sau khi gửi xong
        client.disconnect()
    else:
        print(f"❌ Kết nối thất bại! Mã lỗi: {rc}")

client.on_connect = on_connect

print("⏳ Đang kết nối...")
client.connect(BROKER_URL, PORT)
client.loop_forever() # Chờ gửi xong mới thoát