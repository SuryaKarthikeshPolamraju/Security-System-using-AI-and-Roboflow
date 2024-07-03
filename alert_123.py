from twilio.rest import Client
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
account_sid = '#######################'
auth_token = '####################'
twilio_phone_number = '#################'
recipient_phone_number = '############'
# Message to be sent
message_body =  F"Server running on http://{raspberry_pi_ip}:5000/"

	# Initialize Twilio client and send the message
client = Client(account_sid, auth_token)
message = client.messages.create(
body=message_body,
from_=twilio_phone_number,
to=recipient_phone_number
)

		# Print the SID of the message for reference
print(f"Alert message sent with SID: {message.sid}")
