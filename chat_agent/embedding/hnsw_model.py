# import json
# import os
# import pickle

# import hnswlib
# import numpy as np
# from video_agent.config.global_config import (hnsw_config,
#                                               vector_database_config)
# from video_agent.embedding.encoder_model import LocalEncoderModel
# from video_agent.utils.logger import get_logger


# class HnswModel:
#     def __init__(self, encoder_model: LocalEncoderModel):
#         self.encoder_model = encoder_model
#         self.reset()

#     def reset(self):
#         self.index = hnswlib.Index(
#             space=hnsw_config["space"],
#             dim=hnsw_config["dimension"])
#         self.index.init_index(
#             max_elements=hnsw_config["max_elements"],
#             ef_construction=hnsw_config["ef_construction"],
#             M=hnsw_config["M"],
#         )
#         self.index.set_ef(hnsw_config["ef"])
#         self.code_to_name = {}
#         self.inner_code = 0
#         self.hash_set = set()

#     def get_inner_code(self):
#         self.inner_code += 1
#         return self.inner_code

#     # vec_list 和 code_list 都是 np.array
#     def add_items(self, vec_list, code_list):
#         self.index.add_items(vec_list, code_list)

#     def knn_query(self, vec_list, k=3):
#         return self.index.knn_query(vec_list, k)

#     def has_item(self, name):
#         return name in self.hash_set

#     def add(self, name:str, code=None, real_name=None, embedding=None):
#         self.hash_set.add(name)
#         if code is None:
#             code = self.get_inner_code()
#         code = int(code)
#         if embedding is None:
#             embedding = self.encoder_model.get_embedding(f"{name}")
#         self.add_items([embedding], [code])
#         if real_name is None:
#             self.code_to_name[code] = name
#         else:
#             self.code_to_name[code] = real_name

#     def similarity_search(self, text, k, similarity_threshold, instruction=None):
#         embedding = self.encoder_model.get_embedding(text, instruction=instruction)
#         code_list, distance_list = self.knn_query([embedding], k)
#         code_list = code_list[0].tolist()
#         distance_list = distance_list[0].tolist()
#         result_list = []
#         for code, distance in zip(code_list, distance_list):
#             if distance < similarity_threshold:
#                 result_list.append(dict(
#                     code = str(code),
#                     name = self.code_to_name[code],
#                     distance = distance,
#                 ))
#         result_list.sort(key=lambda p:p["distance"])
#         return result_list

# if __name__ == "__main__":
#     logger = get_logger()
#     encoder_model = LocalEncoderModel(logger)
#     hnsw_model = HnswModel(encoder_model=encoder_model)
#     name_list = [
#         "a",
#         "b",
#     ]
#     for name in name_list:
#         hnsw_model.add(name)
#     temp = hnsw_model.similarity_search("a", k=2, similarity_threshold=1.0)
#     print(temp)

