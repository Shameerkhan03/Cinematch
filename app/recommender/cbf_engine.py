import numpy as np


def recommend_for_user(user_liked_movies, df, similarity, top_n=5):
    liked_titles = set(user_liked_movies)
    combined_scores = np.zeros(len(df))

    for movie in liked_titles:
        if movie in df["title"].values:
            idx = df[df["title"] == movie].index[0]
            combined_scores += similarity[idx]

    if not liked_titles:
        return []

    combined_scores /= len(liked_titles)

    recommendations = sorted(
        list(enumerate(combined_scores)), key=lambda x: x[1], reverse=True
    )

    recommendations = [
        i for i in recommendations if df.iloc[i[0]].title not in liked_titles
    ][:top_n]

    return [
        {"title": df.iloc[i[0]].title, "score": float(i[1])} for i in recommendations
    ]
