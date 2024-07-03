from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
import socket
def get_ip_address():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a well-known server (e.g., Google DNS) to get the local IP address
        sock.connect(('8.8.8.8', 80))
        ip_address = sock.getsockname()[0]  # Get the local IP address
    finally:
        sock.close()

    return ip_address
raspberry_pi_ip = get_ip_address()
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run the Flask app and listen on all network interfaces
    print(f"Server running on http://{raspberry_pi_ip}:5000/")
    app.run(debug=True, host=raspberry_pi_ip)
