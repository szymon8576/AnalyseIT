from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
from helpers import *
import pandas as pd
from lstm_tokenizer.customtokenizer import CustomTokenizer

import dill
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)


# load BERT tokenizer
from transformers import DistilBertTokenizer
bert_tokenizer = DistilBertTokenizer.from_pretrained('./bert_tokenizer')

labels = [word.strip() for word in open("emotions_list.txt", 'r')]
id2label = {i: label for i, label in enumerate(labels)}


# load tokenizer used with LSTM model
with open('lstm_tokenizer/tokenizer.pkl', 'rb') as file:
    lstm_tokenizer = dill.load(file)


def fetch_tf_serve(url, data, data_format="instances"):
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
        tf_serving_url = app.config['TFS_API_URL']+"/v1/models/BERTEmotions:predict"
        tokens = bert_tokenizer(texts, padding="max_length", truncation=True, max_length=64)
        response = fetch_tf_serve(tf_serving_url, dict(tokens), data_format="inputs")
        predictions = np.array(response["outputs"])
        probabilities = sigmoid(predictions)

        result = []
        for text_probabilities in probabilities:
            emotions_and_probs = {id2label[idx]: probability for idx, probability in enumerate(text_probabilities)}
            result.append(emotions_and_probs)

        return result

    elif used_model == "LSTM":
        tf_serving_url = app.config['TFS_API_URL'] + "/v1/models/LSTMSentiment:predict"
        print(tf_serving_url)
        tokenized_texts = [lstm_tokenizer.tokenize(text)[:32] for text in texts]
        print(tokenized_texts)
        padded_tokens = [np.pad(tokens, (0, 32 - len(tokens))).astype(np.int64).tolist() for tokens in tokenized_texts]
        print(padded_tokens)
        response = fetch_tf_serve(tf_serving_url, padded_tokens, data_format="instances")
        print(response)
        probabilities = softmax(response["predictions"])
        print(probabilities)

        result = []
        for text_probabilities in probabilities:
            emotions_and_probs = {label: probability for label, probability in zip(["negative", "neutral", "positive"], text_probabilities)}
            result.append(emotions_and_probs)

        return result

    return f"Model {used_model} not found", 404


@app.route('/analyse', methods=["POST"])
def analyse():
    """
    Endpoint for making predictions on a list of sentences using a specified model.

    :return: JSON response containing the result of the prediction.
    """
    texts, used_model = request.json["texts"], request.json["used_model"]
    result = process_texts(texts, used_model)
    return jsonify(result)


@app.route('/batch_analyse', methods=["POST"])
def batch_analyse():
    texts = request.json["texts"]

    if len(texts) > 20:
        texts = random.sample(texts, 20)

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
