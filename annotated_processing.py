import cv2
from roboflow import Roboflow
import supervision as sv
import subprocess
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, render_template, Response
import time
last_photo_time = time.time()
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
rf = Roboflow(api_key="###############")
project = rf.workspace().project("security-sytem")
model = project.version(3).model
def save_photo(frame):
    global last_photo_time
    timestamp = int(time.time())
    filename = f"unknown.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved photo as: {filename}")
    return filename

def send_email_with_attachment(attachment_path):
    subprocess.call(['python','/home/pi/project/Roboflow/alert.py'])
    sender_email = '###########'
    sender_password = '#############'
    receiver_email = '##################'
    subject = 'Alert: Unknown Person detected'
    message_body = 'Image of the person'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    with open(attachment_path, 'rb') as attachment:
        image_part = MIMEImage(attachment.read(), name=os.path.basename(attachment_path))
    msg.attach(image_part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", str(e))
    last_photo_time = time.time()
    return

app = Flask(__name__)

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        result = model.predict(frame, confidence=40, overlap=30).json()
        predictions = result.get("predictions", [])
        class_name = predictions[0].get('class') if predictions else None
        if(predictions!=[]):
            #print(predictions)
            confidence= predictions[0].get('confidence')
        else:
            confidence = 0
        if((class_name == 'None' or (confidence < 0.50 and confidence != 0) )):
            filename = save_photo(frame)
            send_email_with_attachment(filename)

        labels = [item["class"] for item in result["predictions"]]
        if(confidence < 0.6 and confidence != 0):
            labels = ['Unknown']
        detections = sv.Detections.from_inference(result)
        if(1):
        # Initialize label and bounding box annotators
            label_annotator = sv.LabelAnnotator()
            bounding_box_annotator = sv.BoundingBoxAnnotator()
            annotated_image = bounding_box_annotator.annotate(scene=frame, detections=detections)
            annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
            ima = annotated_image
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            ima = frame
            cv2.imshow('Feed',frame)
            continue
        ret, buffer = cv2.imencode('.jpg', ima)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print(f"Server running on http://{raspberry_pi_ip}:5000/")
    app.run(debug=True, host=raspberry_pi_ip)
    subprocess.call(['python','/home/pi/Desktop/Security-System/alert_123.py'])
