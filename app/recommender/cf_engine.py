import pandas as pd
from sklearn.neighbors import NearestNeighbors


def build_user_movie_matrix(likes_df):
    return (
        likes_df.assign(like=1)
        .pivot_table(index="userId", columns="movieId", values="like")
        .fillna(0)
    )


def recommend_cf(user_id, likes_df, movies_df, top_n=5, k_neighbors=15):
    user_movie_matrix = build_user_movie_matrix(likes_df)

    if user_id not in user_movie_matrix.index:
        raise ValueError("User not found in interaction matrix")

    user_vector = user_movie_matrix.loc[user_id].values.reshape(1, -1)
    knn = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_neighbors=min(k_neighbors + 1, len(user_movie_matrix)),
    )
    knn.fit(user_movie_matrix)

    distances, indices = knn.kneighbors(user_vector)
    sim_users = user_movie_matrix.index[indices.flatten()[1:]]
    sim_distances = distances.flatten()[1:]

    liked_by_user = set(
        user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id] > 0].index
    )
    scores = {}

    for i, sim_user in enumerate(sim_users):
        sim_score = 1 - sim_distances[i]
        sim_likes = user_movie_matrix.loc[sim_user]
        for movie_id in sim_likes[sim_likes > 0].index:
            if movie_id not in liked_by_user:
                scores[movie_id] = scores.get(movie_id, 0) + sim_score

    recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    results = []
    for m, s in recs:
        match = movies_df[movies_df["movieId"] == m]
        if not match.empty:
            title = match.title.values[0]
            results.append({"title": title, "score": float(s)})
    return results
