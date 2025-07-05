import joblib
import boto3
import smtplib
from email.mime.text import MIMEText
import json

# Configuration
S3_BUCKET = 'myawss3formonitoring'
LOG_PREFIX = "logs/"  # Folder in S3
ERROR_CLASSES = {"ERROR", "CRITICAL"}
SEND_NOTIFICATION = True

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'asmitaakolte@gmail.com'

EMAIL_FROM = SMTP_USER
EMAIL_TO = 'asmitaakolte97@gmail.com'

# Load model
model = joblib.load("model/log_classifier.pkl")

# Initialize S3
s3 = boto3.client("s3")

# List all .log files in S3 folder
def list_log_files(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item["Key"] for item in response.get("Contents", []) if item["Key"].endswith(".log")]

# Download and return log lines from a file
def fetch_log_file(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8").splitlines()

# Classify a single line
def classify_log_line(line):
    prediction = model.predict([line])[0]
    print(f"🔍 {line.strip()} ➜ {prediction.upper()}")
    return prediction


def get_smtp_password():
    secret_name = "smtpass"
    region_name = "us-east-1"  # change to your region

    # response = client.get_secret_value(SecretId=secret_name)
    # print("Secrets Manager response:", response)

    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
   # secret_string = response.get("SecretString")
    secret_pass  = json.loads(response["SecretString"])
    print("secret_pass:", secret_pass["SMTP_PASS"])
    return secret_pass["SMTP_PASS"]

# Send email notification
def send_alert(file, lines):
    subject = f"🚨 Alert: Errors found in {file}"
    body = f"The following error lines were detected in {file}:\n\n" + "\n".join(lines[:10])  # first 10 lines
    SMTP_PASS = get_smtp_password()
    msg = MIMEText(body)
    msg["Subject"] = "Email Alert"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            print(f"📧 Email sent to {EMAIL_TO}")
    except Exception as e:
        print(f" Failed to send email: {e}")

# Main logic
def main():
    log_files = list_log_files(S3_BUCKET, LOG_PREFIX)

    for file_key in log_files:
        print(f"\n📂 Scanning: {file_key}")
        lines = fetch_log_file(S3_BUCKET, file_key)
        error_lines = []

        for line in lines:
            prediction = classify_log_line(line)
            if prediction.upper() in ERROR_CLASSES:
                error_lines.append(line)

        if error_lines and SEND_NOTIFICATION:
            send_alert(file_key, error_lines)

if __name__ == "__main__":
    main()
