from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
from helpers import *
import pandas as pd
from lstm_tokenizer.customtokenizer import CustomTokenizer
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)


# load BERT tokenizer
from transformers import DistilBertTokenizer
bert_tokenizer = DistilBertTokenizer.from_pretrained('./bert_tokenizer')

labels = [word.strip() for word in open("emotions_list.txt", 'r')]
id2label = {i: label for i, label in enumerate(labels)}


# load LSTM-model tokenizer
lstm_tokenizer = CustomTokenizer()
lstm_tokenizer.load(dictionary_path="./lstm_tokenizer/dictionary.json", excluded_tokens_path="./lstm_tokenizer/stopwords.json")


def fetch_tf_serving(url, data, data_format="instances"):
    try:
        response = requests.post(url, json={data_format: data})

        if response.status_code == 200:
            return response.json()

        else:
            print(response.json())
            print('Failed to get a valid response from TensorFlow Serving')

    except Exception as e:
        print(str(e))


def process_texts(texts, used_model):
    """
    Processes a list of input texts using the specified sentiment analysis model.

    :param texts: A list of input texts to be analyzed.
    :param used_model: The chosen model for analysis ("BERT" or "LSTM").

    :return: A list containing dictionaries with sentiment or emotion labels and their corresponding probabilities.

    """
    if used_model == "BERT":
        tf_serving_url = app.config['TFS_BERT_URL']+"/v1/models/DistilBERTEmotions:predict"
        tokens = bert_tokenizer(texts, padding="max_length", truncation=True, max_length=64)
        response = fetch_tf_serving(tf_serving_url, dict(tokens), data_format="inputs")
        predictions = np.array(response["outputs"])
        probabilities = sigmoid(predictions)

        result = []
        for text_probabilities in probabilities:
            emotions_and_probs = {id2label[idx]: probability for idx, probability in enumerate(text_probabilities)}
            result.append(emotions_and_probs)

        return result

    elif used_model == "LSTM":
        tf_serving_url = app.config['TFS_LSTM_URL'] + "/v1/models/LSTMSentiment:predict"
        tokenized_texts = [lstm_tokenizer.tokenize(text)[:32] for text in texts]
        padded_tokens = [np.pad(tokens, (0, 32 - len(tokens))).astype(np.int64).tolist() for tokens in tokenized_texts]
        response = fetch_tf_serving(tf_serving_url, padded_tokens, data_format="instances")
        probabilities = softmax(response["predictions"])

        result = []
        for text_probabilities in probabilities:
            emotions_and_probs = {label: probability for label, probability in zip(["negative", "neutral", "positive"], text_probabilities)}
            result.append(emotions_and_probs)

        return result

    return f"Model {used_model} not found", 404


@app.route('/classify-sentences', methods=["POST"])
def classify_sentences():
    """
    Endpoint for making predictions on a list of sentences using a specified model.

    :return: JSON response containing the result of the prediction.
    """
    texts, used_model = request.json["texts"], request.json["used_model"]
    result = process_texts(texts, used_model)
    return jsonify(result)


@app.route('/generate-report', methods=["POST"])
def generate_report():
    """
    Endpoint for generating a comprehensive report based on the analysis of emotions and sentiment in a list of texts.

    The analysis involves the BERT model for emotions and the LSTM model for sentiment.
    If there are more than 30 texts, a random sample of 30 texts is used for analysis.

    :return: JSON response containing the result of the analysis.
    """
    texts = request.json["texts"]

    # The operations below are computationally demanding.
    # If there are more than 30 texts, randomly sample them.
    if len(texts) > 30:
        texts = random.sample(texts, 30)

    result = {}

    # Analyse emotions
    emotions_data = process_texts(texts, "BERT")
    emotions_df = pd.DataFrame.from_dict(emotions_data)
    emotions_percentages = emotions_df.applymap(lambda x: 1 if x > 0.2 else 0).sum(axis=0) / len(texts)
    result["emotions"] = emotions_percentages.to_dict()

    # Find sentences with most positive and most negative sentiment
    sentiment_data = process_texts(texts, "LSTM")
    sentiment_df = pd.DataFrame.from_dict(sentiment_data)
    result["most_positive"], result["most_negative"] = texts[sentiment_df['positive'].idxmax()], texts[sentiment_df['negative'].idxmax()]

    # Analyse sentiment
    max_columns = sentiment_df.idxmax(axis=1)
    column_counts = max_columns.value_counts()
    sentiment_result = (column_counts / len(max_columns))
    result["sentiment"] = sentiment_result.to_dict()

    # Combine results into full report
    full_report = pd.DataFrame({"text": texts})
    full_report = pd.concat([full_report, emotions_df, sentiment_df.add_prefix("sentiment_")], axis=1)
    result["full_report"] = full_report.to_json(orient='records', lines=True, indent=2)

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
