from functools import reduce

import pytest

from utils.merge_dicts import merge_dicts


@pytest.mark.parametrize(
    "list_of_dicts,expected_result",
    [
        [[{}, {}], {}],
        [[{"k1": "v1"}, {}], {"k1": "v1"}],
        [[{"k1": "v1"}, {"k2": "v2"}], {"k1": "v1", "k2": "v2"}],
        [[{"k1": "v1"}, {"k1": "v2"}], {"k1": "v2"}],
        [[{"k1": 1}, {"k1": "v2"}], {"k1": "v2"}],
        [[{"k1": "v1", "k3": "v3"}, {"k1": "v2"}], {"k1": "v2", "k3": "v3"}],
        [
            [{"k1": "v1", "k3": "v3"}, {"k1": "v2", "k4": "v4"}],
            {"k1": "v2", "k3": "v3", "k4": "v4"},
        ],
        [[{"k1": {"k10": "v1"}}, {"k1": "v2"}], {"k1": "v2"}],
        [
            [{"k1": {"k10": "v1", "k20": "v3"}}, {"k1": {"k10": "v2"}}],
            {"k1": {"k10": "v2", "k20": "v3"}},
        ],
        [[{"k1": "v1"}, {"k1": "v1"}], {"k1": "v1"}],
    ],
)
def test_merge_dicts_direct(list_of_dicts, expected_result):
    assert dict(merge_dicts(*list_of_dicts)) == expected_result


@pytest.mark.parametrize(
    "list_of_dicts,expected_result",
    [
        [[{}, {}], {}],
        [[{"k1": "v1"}, {}], {"k1": "v1"}],
        [[{"k1": "v1"}, {"k2": "v2"}], {"k1": "v1", "k2": "v2"}],
        [[{"k1": "v1"}, {"k1": "v2"}], {"k1": "v2"}],
        [[{"k1": 1}, {"k1": "v2"}], {"k1": "v2"}],
        [[{"k1": "v1", "k3": "v3"}, {"k1": "v2"}], {"k1": "v2", "k3": "v3"}],
        [
            [{"k1": "v1", "k3": "v3"}, {"k1": "v2", "k4": "v4"}],
            {"k1": "v2", "k3": "v3", "k4": "v4"},
        ],
        [
            [{"k1": "v1"}, {"k1": "v2", "k4": "v4"}, {"k3": "v3"}],
            {"k1": "v2", "k4": "v4", "k3": "v3",},
        ],
        [
            [{"k1": "v1"}, {"k1": "v2", "k4": "v4"}, {"k3": "v3", "k4": "override"}],
            {"k1": "v2", "k3": "v3", "k4": "override",},
        ],
        [
            [
                {"k1": "v1", "k4": "init"},
                {"k1": "v2", "k4": "v4"},
                {"k3": "v3", "k4": "override"},
            ],
            {"k1": "v2", "k3": "v3", "k4": "override",},
        ],
    ],
)
def test_merge_dicts_reduce(list_of_dicts, expected_result):
    assert dict(reduce(merge_dicts, list_of_dicts)) == expected_result
