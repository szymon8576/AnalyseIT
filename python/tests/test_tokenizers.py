def test_lstm_tokenizer(tokenizers):
    tokens = tokenizers["lstm_tokenizer"].tokenize("LSTM-tokenizer test message!")

    assert len(tokens) > 0
    assert all([type(token) == int for token in tokens])


def test_bert_tokenizer(tokenizers):
    result = tokenizers["bert_tokenizer"](["BERT-tokenizer test message!"])

    assert "input_ids" in result.keys() and "attention_mask" in result.keys()
    assert len(result["input_ids"][0]) > 0
    assert all([type(token) == int for token in result["input_ids"][0]])