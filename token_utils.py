import tiktoken

def count_tokens(text, encoding_name="gpt-4"):
    """
    Count the number of tokens in a given text using tiktoken.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

def chunk_text(text, max_tokens=3000, encoding_name="gpt-4"):
    """
    Split the text into chunks where each chunk has at most 'max_tokens'.
    Yields decoded text chunks.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        yield encoding.decode(chunk_tokens) 