from collections import Counter
from typing import Any


class MetricsAccumulator(object):
    def __init__(self):
        self.tracks: dict[str, list[int]] = {}

    def update(self, frame: dict[str, Any]) -> None:
        for detection in frame['data']:
            if not detection['bounding_box']:
                continue
            if detection['cb_id'] not in self.tracks:
                self.tracks[detection['cb_id']] = []
            self.tracks[detection['cb_id']].append(detection['track_id'])

    def compute(self) -> dict[str, float]:
        if not self.tracks:
            raise ValueError('Tracks are empty. Call update() first.')

        return {
            'Average track coverage': self.average_track_coverage(),
            'Mismatch ratio': self.mismatch_ratio(),
        }

    def average_track_coverage(self) -> float:
        coverages = []
        for track in self.tracks.values():
            coverages.append(self._get_coverage(track))
        return sum(coverages) / len(coverages)

    def mismatch_ratio(self) -> float:
        detections, errors = 0, 0
        for track in self.tracks.values():
            errors += self._get_mismatch_errors(track)
            detections += len(track)
        return 1 - (errors / detections)

    def _get_coverage(self, track: list[int]) -> float:
        _, count = Counter(track).most_common(1)[0]
        return count / len(track)

    def _get_mismatch_errors(self, track: list[int]) -> int:
        if len(track) < 2:
            return 0
        errors = 0
        for idx in range(1, len(track)):
            if track[idx] != track[idx - 1]:
                errors += 1
        return errors
