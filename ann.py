from flask import Flask, render_template, Response
import cv2
import test
import os
import subprocess
app = Flask(__name__)
subprocess.run(['python','test.py'])
def gen_frames():
    while True:
        frame = test.annotated_image
        if frame is None:
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
    # Run the Flask app on the Raspberry Pi's Wi-Fi network
    app.run(host='192.168.1.9', port=5000, debug=True)
