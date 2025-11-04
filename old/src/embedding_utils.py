import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def generate_embedding(text: str) -> np.ndarray:
    """
    Generates an embedding for the given text using a pre-trained SentenceTransformer model.
    The embedding dimension will depend on the chosen model (e.g., 768 for 'paraphrase-multilingual-mpnet-base-v2').

    Args:
        text: The input text (product name) to generate an embedding for.

    Returns:
        A numpy array representing the embedding.
    """
    if not text or not isinstance(text, str):
        # This ensures the norm is not zero, avoiding division by zero.
        return np.ones(model.get_sentence_embedding_dimension(), dtype=np.float32)

    # Encode the text to get the embedding
    embeddings = model.encode(text, convert_to_tensor=False)
    return embeddings
