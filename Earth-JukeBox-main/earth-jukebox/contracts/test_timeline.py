import unittest

from contracts.timeline import (
    MAX_DURATION_SECONDS,
    PlaybackState,
    PlaybackTimeline,
    TimelineContractError,
    parse_timeline_contract,
)


class TimelineTests(unittest.TestCase):
    def test_play_pause_resume_preserve_position(self):
        timeline = PlaybackTimeline(10)
        timeline.play()
        timeline.advance(2)
        self.assertEqual(timeline.pause().position_seconds, 2)
        self.assertEqual(timeline.snapshot().state, PlaybackState.PAUSED)
        timeline.resume()
        timeline.advance(1)
        self.assertEqual(timeline.snapshot().position_seconds, 3)

    def test_stop_resets_position_and_state(self):
        timeline = PlaybackTimeline(10)
        timeline.play()
        timeline.advance(4)
        snapshot = timeline.stop()
        self.assertEqual(snapshot.position_seconds, 0)
        self.assertEqual(snapshot.state, PlaybackState.STOPPED)

    def test_restart_resets_and_starts(self):
        timeline = PlaybackTimeline(10)
        timeline.play()
        timeline.advance(4)
        snapshot = timeline.restart()
        self.assertEqual(snapshot.position_seconds, 0)
        self.assertEqual(snapshot.state, PlaybackState.PLAYING)

    def test_seek_is_bounded_and_end_pauses(self):
        timeline = PlaybackTimeline(10)
        timeline.play()
        timeline.seek(7)
        self.assertEqual(timeline.snapshot().position_seconds, 7)
        snapshot = timeline.seek(10)
        self.assertEqual(snapshot.state, PlaybackState.PAUSED)
        with self.assertRaisesRegex(TimelineContractError, "within"):
            timeline.seek(11)

    def test_speed_changes_elapsed_time_deterministically(self):
        timeline = PlaybackTimeline(10, speed=2)
        timeline.play()
        timeline.advance(1.5)
        self.assertEqual(timeline.snapshot().position_seconds, 3)
        timeline.set_speed(0.5)
        timeline.advance(2)
        self.assertEqual(timeline.snapshot().position_seconds, 4)

    def test_advance_does_not_move_when_not_playing(self):
        timeline = PlaybackTimeline(10)
        timeline.advance(5)
        self.assertEqual(timeline.snapshot().position_seconds, 0)
        timeline.play()
        timeline.pause()
        timeline.advance(5)
        self.assertEqual(timeline.snapshot().position_seconds, 0)

    def test_completion_is_clamped_and_paused(self):
        timeline = PlaybackTimeline(3)
        timeline.play()
        snapshot = timeline.advance(1000)
        self.assertEqual(snapshot.position_seconds, 3)
        self.assertEqual(snapshot.state, PlaybackState.PAUSED)

    def test_invalid_duration_speed_and_elapsed_are_rejected(self):
        with self.assertRaises(TimelineContractError):
            PlaybackTimeline(0)
        with self.assertRaises(TimelineContractError):
            PlaybackTimeline(MAX_DURATION_SECONDS + 1)
        timeline = PlaybackTimeline(10)
        with self.assertRaises(TimelineContractError):
            timeline.set_speed(0)
        with self.assertRaises(TimelineContractError):
            timeline.advance(-1)

    def test_schema_parser_is_dataset_agnostic(self):
        snapshot = parse_timeline_contract(
            {
                "schema_version": "playback-timeline.v1",
                "duration_seconds": 30,
                "position_seconds": 5,
                "speed": 1.5,
                "state": "paused",
            }
        )
        self.assertEqual(snapshot.state, PlaybackState.PAUSED)
        self.assertEqual(snapshot.position_seconds, 5)


if __name__ == "__main__":
    unittest.main()
