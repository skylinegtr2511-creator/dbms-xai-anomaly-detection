import re
import json

def load_vocab(vocab_path):
    with open(vocab_path, 'r') as f:
        return json.load(f)

def tokenize_sql(query):
    query = str(query).lower()
    query = re.sub(r'([^\w\s])', r' \1 ', query)
    return query.split()

def encode_query(query, word2idx, max_length=100):
    tokens = tokenize_sql(query)
    seq = [word2idx.get(word, word2idx.get('<UNK>', 1)) for word in tokens]
    
    if len(seq) < max_length:
        seq += [word2idx.get('<PAD>', 0)] * (max_length - len(seq))
    else:
        seq = seq[:max_length]
    return seq