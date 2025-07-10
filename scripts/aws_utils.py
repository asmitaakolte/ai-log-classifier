import boto3
import json

def get_s3_client():
    return boto3.client("s3")

def get_secrets_client(region):
    return boto3.client("secretsmanager", region_name=region)

def fetch_secret(secret_name, region):
    client = get_secrets_client(region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except Exception as e:
        print(f"❌ Failed to retrieve secret: {e}")
        return None

def list_log_files(s3, bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item["Key"] for item in response.get("Contents", []) if item["Key"].endswith(".log")]

def fetch_log_file(s3, bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8").splitlines()