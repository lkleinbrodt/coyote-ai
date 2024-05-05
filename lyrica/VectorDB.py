# just a quick first implementation!
import numpy as np


class Dictbased_VectorDB:
    def __init__(self, embeddings={}, lyrics={}):
        self.internal_store = embeddings
        self.inverse_index = {}  # An indexing structure for retrieval
        self.lyrics_dict = lyrics

    def calculate_squared_euclidean(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def calculate_average_embedding(self, exclude_similar=False):

        if not exclude_similar:
            return np.mean(list(self.internal_store.values()), axis=0)

        # first, discard any vectors that are too similar to each other
        # TODO: improve on this approach
        # This doesnt really work
        np_embeddings = np.array(list(self.internal_store.values()))

        # calculate the pairwise distances
        distances = np.linalg.norm(
            np_embeddings[:, None] - np_embeddings[None, :], axis=2
        )
        # find the indices of the vectors that are too similar
        invalid_indices = ((distances < 0.25) & (distances != 0)).sum(axis=1) > 0

        # remove the similar vectors
        np_embeddings = np_embeddings[~invalid_indices, :]

        return np.mean(np_embeddings, axis=0)

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

    def __len__(self):
        return len(self.internal_store)

    def get_top_lyrics(self):
        avg_embedding = self.calculate_average_embedding(exclude_similar=True)

        search_results = self.get_knn_byitem(avg_embedding, num_nbrs=3)
        ids = [result[0] for result in search_results]

        top_lyrics = [self.lyrics_dict[lyric_id] for lyric_id in ids]

        return top_lyrics
