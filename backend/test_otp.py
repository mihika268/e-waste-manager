import requests
import json

# Test OTP functionality
print('Testing OTP generation...')

# Send OTP
response = requests.post('http://localhost:5000/api/auth/send-otp', json={
    'email': 'test@example.com'
})
print(f'Send OTP response: {response.status_code}')
print(f'Response headers: {response.headers}')
print(f'Response text: {response.text}')
if response.status_code == 200:
    try:
        result = response.json()
        print(f'Response JSON: {result}')
        if 'otp_code' in result:
            print(f'Generated OTP: {result["otp_code"]}')
        else:
            print('No otp_code found in response')
    except Exception as e:
        print(f'Error parsing JSON: {e}')
else:
    print(f'Error: {response.text}')