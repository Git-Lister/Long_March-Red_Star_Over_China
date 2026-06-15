"""Tests for src.core.utils."""

import json
import os
import tempfile

import pytest

from src.core.utils import clamp, load_json, save_json, weighted_choice


class TestClamp:
    def test_within_range(self):
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_below_min(self):
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_above_max(self):
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_inverted_bounds_raises(self):
        with pytest.raises(ValueError):
            clamp(5.0, 10.0, 0.0)


class TestWeightedChoice:
    def test_returns_expected_type(self):
        result = weighted_choice(["a", "b", "c"], [1, 1, 1])
        assert result in ["a", "b", "c"]

    def test_deterministic_high_weight(self):
        result = weighted_choice(["a", "b"], [1000, 1])
        assert result == "a"

    def test_empty_choices_raises(self):
        with pytest.raises(ValueError):
            weighted_choice([], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            weighted_choice(["a", "b"], [1])

    def test_all_zero_weights_raises(self):
        with pytest.raises(ValueError):
            weighted_choice(["a", "b"], [0, 0])


class TestJsonIO:
    def test_save_and_load(self):
        data = {"key": "value", "list": [1, 2, 3]}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.json")
            save_json(path, data)
            loaded = load_json(path)
            assert loaded == data

    def test_save_creates_directories(self):
        data = {"hello": "world"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "subdir", "test.json")
            save_json(path, data)
            assert os.path.exists(path)
            loaded = load_json(path)
            assert loaded == data
