from config_loader import load_config
from aws_utils import get_s3_client, fetch_log_file, list_log_files, fetch_secret
from email_utils import send_email
from classifier import load_model_and_vectorizer, classify_line

ERROR_CLASSES = set()

def send_alert(config, file, error_lines):
    subject = f"🚨 Alert: Errors found in {file}"
    body = f"The following errors were found in {file}:\n\n" + "\n".join(error_lines[:10])
    
    smtp_pass = fetch_secret(config["smtp"]["secret_name"], config["smtp"]["region"]).get("SMTP_PASS")
    if not smtp_pass:
        print("❌ SMTP password unavailable. Skipping email.")
        return

    send_email(
        config["smtp"]["server"],
        config["smtp"]["port"],
        config["smtp"]["user"],
        smtp_pass,
        config["smtp"]["user"],
        config["smtp"]["to"],
        subject,
        body
    )

def main():
    config = load_config()
    global ERROR_CLASSES
    ERROR_CLASSES = set(label.upper() for label in config["notification"]["error_classes"])

    s3 = get_s3_client()
    model, vectorizer = load_model_and_vectorizer()
    #model = load_model_and_vectorizer()
    log_files = list_log_files(s3, config["s3"]["bucket"], config["s3"]["prefix"])

    for file_key in log_files:
        print(f"\n📂 Scanning: {file_key}")
        lines = fetch_log_file(s3, config["s3"]["bucket"], file_key)
        error_lines = []

        for line in lines:
            prediction = classify_line(model, vectorizer, line)
            if prediction.upper() in ERROR_CLASSES:
                error_lines.append(line)

        if error_lines and config["notification"]["enabled"]:
            send_alert(config, file_key, error_lines)

if __name__ == "__main__":
    main()
