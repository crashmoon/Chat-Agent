import numpy as np
from chat_agent.config.global_config import encoder_config
from transformers import AutoModel, AutoTokenizer


class LocalEncoderModel:
    def __init__(self):
        self.device = encoder_config["device"]
        self.model_name = encoder_config["model_name"]
        self.embedding_map = {}
        if self.use_local:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)

    # sequence is original text, support different language
    def get_embedding(self, sequence: str):
        inputs = self.tokenizer(sequence, return_tensors="pt").to(self.device)
        outputs =  self.model(**inputs)
        embedding = outputs.pooler_output[0]
        return embedding.tolist()

    # 使用 numpy 计算余弦相似度
    def get_cosine_similarity(self, embedding1: list, embedding2: list):
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        cos = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return cos

    def get_distance(self, name1, name2):
        embedding1 = self.get_embedding(name1)
        embedding2 = self.get_embedding(name2)
        return 1.0 - self.get_cosine_similarity(embedding1, embedding2)


if __name__=="__main__":
    model = LocalEncoderModel()
    print(len(model.get_embedding("Hello world")))



