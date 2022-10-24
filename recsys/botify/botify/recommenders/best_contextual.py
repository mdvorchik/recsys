from .random import Random
from .recommender import Recommender
import random

from .top_pop import TopPop


class BestContextual(Recommender):
    """
    Recommend tracks closest to the previous one or popular.
    """

    def __init__(self, tracks_redis, catalog):
        self.tracks_redis = tracks_redis
        self.toppop = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.fallback = Random(tracks_redis)
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.toppop.recommend_next(user, prev_track, prev_track_time)

        if prev_track_time > 0.6:
            previous_track = self.catalog.from_bytes(previous_track)
            recommendations = previous_track.recommendations
            if not recommendations:
                return self.fallback.recommend_next(user, prev_track, prev_track_time)
            shuffled = list(recommendations[:10])
            random.shuffle(shuffled)
            return shuffled[0]
        else:
            return self.toppop.recommend_next(user, prev_track, prev_track_time)
