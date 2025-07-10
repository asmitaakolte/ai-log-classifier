import os
import mlflow
import boto3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
from aws_utils import get_s3_client, fetch_log_file, list_log_files



def load_training_data_from_s3(s3, bucket, prefix):
    """
    Loads training data using existing aws_utils functions.
    Assumes files are stored in paths like:
      train/error/file1.log
      train/warning/file2.log
      train/info/file3.log
    Returns:
      texts: list of log lines
      labels: corresponding list of labels (extracted from folder name)
    """
    texts = []
    labels = []

    log_files = list_log_files(s3, bucket, prefix)

    for file_key in log_files:
        # Example file_key: train/error/file1.log
        for file_key in log_files:
            lines = fetch_log_file(s3, bucket, file_key)
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Basic label detection from content
                line_upper = line.upper()
                if "ERROR" in line_upper:
                    label = "error"
                elif "WARNING" in line_upper:
                    label = "warning"
                elif "INFO" in line_upper:
                    label = "info"
                else:
                    continue  # skip unknowns

                texts.append(line)
                labels.append(label)

            return texts, labels



from config_loader import load_config

def train_and_save_model():
    config = load_config()
    bucket = config["s3"]["bucket"]
    prefix = config["s3"]["prefix"]
    s3 = get_s3_client()

    texts, labels = load_training_data_from_s3(s3, bucket, prefix)
    if not texts or not labels:
        print("❌ No training data found. Please check your S3 bucket and prefix.")
        return
    # Split data just for evaluation
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=42)

    # Create vectorizer
    vectorizer = TfidfVectorizer()

    # Fit vectorizer and transform training data
    X_train_vec = vectorizer.fit_transform(X_train)

    # Train model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    # Evaluate on test set
    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    print(classification_report(y_test, y_pred))

    # Save model and vectorizer
    os.makedirs('model', exist_ok=True)
    joblib.dump(vectorizer, 'model/vectorizer.pkl')
    joblib.dump(model, 'model/log_classifier.pkl')
    print("Model and vectorizer saved in 'model/' folder.")

    # Start MLflow tracking
    with mlflow.start_run(run_name="LogClassifierTFIDF"):
        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_param("vectorizer", "Tfidf")
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))

        model.fit(X_train_vec, y_train)

        # Evaluate
        X_test_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_test_vec)

        mlflow.log_metric("precision", precision_score(y_test, y_pred, average="weighted"))
        mlflow.log_metric("recall", recall_score(y_test, y_pred, average="weighted"))
        mlflow.log_metric("f1", f1_score(y_test, y_pred, average="weighted"))

        # Save and log artifacts
        os.makedirs('model', exist_ok=True)
        joblib.dump(vectorizer, 'model/vectorizer.pkl')
        joblib.dump(model, 'model/model.pkl')
        mlflow.log_artifact('model/vectorizer.pkl')
        mlflow.log_artifact('model/model.pkl')

        # Optional: register model
        # mlflow.sklearn.log_model(model, "sklearn-model", registered_model_name="LogClassifierModel")

        print("✅ Training completed and logged to MLflow.")

if __name__ == "__main__":
    train_and_save_model()

