from flask import Flask, jsonify, render_template
from smtp_build import send_email_diy
import json

app = Flask(__name__)

def load_config(filename='configemail.json'):
    try:
        with open(filename, 'r') as json_file:
            config_data = json.load(json_file)
            emails_info = config_data.get('email', [])
            user_emails = []
            user_passwords = []
            for email_info in emails_info:
                user_emails.append(email_info.get('username', ''))
                user_passwords.append(email_info.get('password', ''))
            return user_emails, user_passwords
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return [], []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {filename}: {e}")
        return [], []

def load_text_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return ""

def load_email_data():
    try:
        with open('receive.txt', 'r') as file:
            recipients = [line.strip() for line in file if line.strip()] 
            if not recipients:
                raise ValueError("No recipients found in receive.txt")
            
        sub_data = load_text_file('sub.txt').split(',')
        subject = sub_data[0].strip()
        content = sub_data[1].strip()

        return recipients, subject, content
    except Exception as e:
        print(f"Error loading email data: {str(e)}")
        return [], "", ""

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/automation', methods=['POST'])
def automation():
    user_emails, user_passwords = load_config()
    recipients, subject, content = load_email_data()

    try:
        for recipient in recipients:
            for user_email, user_password in zip(user_emails, user_passwords):
                send_email_diy(user_email, user_password, recipient, content, subject)
        return jsonify({"message": "Emails sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Error sending email: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
