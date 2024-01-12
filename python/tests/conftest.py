import pytest
from app import app as app_, lstm_tokenizer, bert_tokenizer


@pytest.fixture
def flask_app():
    return app_


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def tokenizers():
    return {'lstm_tokenizer': lstm_tokenizer, 'bert_tokenizer': bert_tokenizer}
