# just a quick first implementation!
import numpy as np


class Dictbased_VectorDB:
    def __init__(self, embeddings={}):
        self.internal_store = embeddings
        self.inverse_index = {}  # An indexing structure for retrieval

    def calculate_squared_euclidean(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def calculate_average_embedding(self):
        return np.mean(list(self.internal_store.values()), axis=0)

    def add_item(self, new_id, new_item):
        self.internal_store[new_id] = new_item

        # measure euclidean distance of the new vector from every existing vector
        # this precomputation improves the efficiency of the get_knn operation if
        # existing queries are searched for.
        for stored_index, stored_item in self.internal_store.items():
            similarity = self.calculate_squared_euclidean(new_item, stored_item)

            if stored_index not in self.inverse_index:
                self.inverse_index[stored_index] = {}
            self.inverse_index[stored_index][new_id] = similarity

    def get_knn_byitem(self, query_vector, num_nbrs=5):
        knn = []

        for stored_index, stored_item in self.internal_store.items():
            similarity = self.calculate_squared_euclidean(query_vector, stored_item)
            # print(
            #     "Similarity between {0} and {1} is: {2}".format(
            #         query_vector, stored_item, similarity
            #     )
            # )
            knn.append((stored_index, stored_item, similarity))

        knn.sort(key=lambda x: x[1])

        # Return the top N results
        return knn[:num_nbrs]

    def get_knn_byid(self, query_vector_id=0, num_nbrs=5):
        # if this query vector id doesn't exist in the database, then return None
        if query_vector_id not in self.internal_store:
            return ""

        knn = []

        for stored_index, stored_item in self.internal_store.items():
            if stored_index == query_vector_id:
                continue

            similarity = self.inverse_index[stored_index][query_vector_id]
            knn.append((stored_item, similarity))

        knn.sort(key=lambda x: x[1])

        # Return the top N results
        return knn[:num_nbrs]
