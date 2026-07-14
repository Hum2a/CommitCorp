"""Commit message corpus tests."""

from __future__ import annotations

import unittest

from commit_machine.commit_messages import COMMIT_MESSAGES, CommitMessageProvider


class CommitMessageTests(unittest.TestCase):
    def test_minimum_pool_size(self) -> None:
        self.assertGreaterEqual(len(COMMIT_MESSAGES), 250)

    def test_unique(self) -> None:
        self.assertEqual(len(COMMIT_MESSAGES), len(set(COMMIT_MESSAGES)))

    def test_sequential_provider(self) -> None:
        provider = CommitMessageProvider(mode="sequential", start_index=0)
        first = provider.next_message()
        second = provider.next_message()
        self.assertEqual(first, COMMIT_MESSAGES[0])
        self.assertEqual(second, COMMIT_MESSAGES[1])


if __name__ == "__main__":
    unittest.main()
