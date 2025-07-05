import boto3
from datetime import datetime
import os

s3 = boto3.client('s3')
bucket_name = 'myawss3formonitoring'
prefix = 'logs/'

def find_all_log_files():
    for obj in response.get('Contents', []):
        key = obj['Key']
        file_name = os.path.basename(key)
        s3.download_file(bucket, key, f"./{file_name}")
        print(f"Downloaded: {file_name}")

if __name__ == "__main__":
    log_files = find_all_log_files()
    if not log_files:
        print("No log files found.")
    else:
        for log_file in log_files:
            timestamped_key = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{os.path.basename(log_file)}"
            try:
                s3.upload_file(log_file, bucket_name, timestamped_key)
                print(f"Log file {log_file} uploaded to s3://{bucket_name}/{timestamped_key}")
            except Exception as e:
                print(f"Failed to upload {log_file}: {e}")
    s3.upload_file(log_file, bucket_name, timestamped_key)
    print(f"Log file {log_file} uploaded to s3://{bucket_name}/{timestamped_key}")