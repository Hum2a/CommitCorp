"""SemVer-from-commits policy tests."""

from __future__ import annotations

import unittest

from commit_machine.version_manager import VersionManager


class VersionManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vm = VersionManager()

    def test_zero(self) -> None:
        v = self.vm.from_commits(0)
        self.assertEqual(v.label, "v0.0.0")

    def test_patch_boundary(self) -> None:
        self.assertEqual(self.vm.from_commits(999).label, "v0.0.0")
        self.assertEqual(self.vm.from_commits(1000).label, "v0.0.1")
        self.assertEqual(self.vm.from_commits(1999).label, "v0.0.1")
        self.assertEqual(self.vm.from_commits(2000).label, "v0.0.2")

    def test_minor_boundary(self) -> None:
        self.assertEqual(self.vm.from_commits(10_000).label, "v0.1.0")
        self.assertEqual(self.vm.from_commits(11_000).label, "v0.1.1")

    def test_major_boundary(self) -> None:
        self.assertEqual(self.vm.from_commits(100_000).label, "v1.0.0")
        self.assertEqual(self.vm.from_commits(110_000).label, "v1.1.0")
        self.assertEqual(self.vm.from_commits(111_000).label, "v1.1.1")

    def test_detect_bump(self) -> None:
        bump = self.vm.detect_bump(999, 1000)
        self.assertEqual(bump.kind, "patch")
        bump = self.vm.detect_bump(9999, 10000)
        self.assertEqual(bump.kind, "minor")
        bump = self.vm.detect_bump(99999, 100000)
        self.assertEqual(bump.kind, "major")
        bump = self.vm.detect_bump(100, 101)
        self.assertEqual(bump.kind, "none")

    def test_codename(self) -> None:
        self.assertIn(
            "Historical Persistence",
            self.vm.from_commits(100_000).codename,
        )


if __name__ == "__main__":
    unittest.main()
