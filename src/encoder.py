import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
import torch


class EncoderModel:
    """Wrapper class for the HuggingFace AutoModel and AutoTokenizer for Custom Encoder Model"""
    def __init__(self, model_name):
        """Initialize the model and tokenizer"""
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)

    def chunk_text(self, text, max_length=256):
        """Split text into chunks of a maximum length"""
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    def encode_batch(self, text_batch):
        """Encode a batch of text"""
        with torch.no_grad():
            out = self.model(
                **self.tokenizer(text_batch, return_tensors="pt", max_length=self.model.config.max_position_embeddings,
                                 truncation=True, padding=True).to(self.device))
        return out

    def encode_text(self, text_list, batch_size=32):
        """Encode a list of text"""
        encodings = np.zeros((len(text_list), 768))
        for i in tqdm(range(0, len(text_list), batch_size), desc="Encoding passages"):
            text_batch = text_list[i:i + batch_size]
            encodings_batch = self.encode_batch(text_batch)
            encodings[i:i + batch_size] = encodings_batch.last_hidden_state[:, 0, :].cpu().numpy()
        return encodings
