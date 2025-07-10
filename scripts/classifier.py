import joblib

def load_model_and_vectorizer():
    # Adjust path based on your project root
    # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # go up from scripts/
    # vectorizer_path = os.path.join(base_dir, 'model', 'vectorizer.pkl')
    # model_path = os.path.join(base_dir, 'model', 'model.pkl')


    # vectorizer = joblib.load(vectorizer_path)
    # model = joblib.load(model_path)
    # return model, vectorizer
    model_path = 'model/log_classifier.pkl'
    model = joblib.load(model_path)
    return model

def classify_line(model, vectorizer, line):
    X_vec = vectorizer.transform([line])
    prediction = model.predict(X_vec)[0]
    return prediction
