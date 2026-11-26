import asyncio
from types import SimpleNamespace

import pandas as pd
import pytest
from telethon.tl.types import ReactionPaid

from sort_reactions import _message_link, _reaction_label, _top_records


class FakeClient:
    def __init__(self, docs=None, error=None):
        self.docs = docs if docs is not None else []
        self.error = error
        self.calls = 0

    async def __call__(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return self.docs


def test_top_records_returns_top_n_in_sorted_order():
    df = pd.DataFrame([
        {'id': 3, 'date': pd.Timestamp('2025-01-03', tz='UTC'), 'total_reactions': 30,
         'breakdown': '👍: 30', 'views': 300, 'forwards': 3, 'velocity': 3.456,
         'text': 'third', 'link': 'https://t.me/c/1/3'},
        {'id': 2, 'date': pd.Timestamp('2025-01-02', tz='UTC'), 'total_reactions': 20,
         'breakdown': '👍: 20', 'views': 200, 'forwards': 2, 'velocity': 2.0,
         'text': 'second', 'link': 'https://t.me/c/1/2'},
        {'id': 1, 'date': pd.Timestamp('2025-01-01', tz='UTC'), 'total_reactions': 10,
         'breakdown': '👍: 10', 'views': 100, 'forwards': 1, 'velocity': 1.0,
         'text': 'first', 'link': 'https://t.me/c/1/1'},
    ])

    records = _top_records(df, 2)

    assert [r['id'] for r in records] == [3, 2]
    assert records[0]['total_reactions'] == 30
    assert records[0]['velocity'] == 3.456
    assert records[0]['text'] == 'third'
    assert records[0]['link'] == 'https://t.me/c/1/3'
    assert isinstance(records[0]['id'], int)
    assert isinstance(records[0]['views'], int)


def test_top_records_turns_missing_and_nan_values_into_defaults():
    nan = float('nan')
    df = pd.DataFrame([{
        'id': 1,
        'date': nan,
        'total_reactions': 5,
        'breakdown': nan,
        'views': nan,
        'forwards': nan,
        'velocity': nan,
        'text': nan,
        'link': nan,
    }])

    record = _top_records(df, 1)[0]

    assert record['breakdown'] == 'None'
    assert record['views'] == 0
    assert record['forwards'] == 0
    assert record['velocity'] == 0.0
    assert record['text'] == ''
    assert record['link'] == ''


def test_top_records_handles_missing_optional_columns():
    df = pd.DataFrame([{'id': 7, 'date': '2025-01-01', 'total_reactions': 3}])

    record = _top_records(df, 1)[0]

    assert record['id'] == 7
    assert record['breakdown'] == 'None'
    assert record['views'] == 0
    assert record['forwards'] == 0
    assert record['velocity'] == 0.0
    assert record['text'] == ''
    assert record['link'] == ''


def test_top_records_returns_empty_for_zero_top_n():
    df = pd.DataFrame([{'id': 1, 'date': '2025-01-01', 'total_reactions': 1}])

    assert _top_records(df, 0) == []


def test_top_records_returns_all_when_top_n_exceeds_rows():
    df = pd.DataFrame([
        {'id': 1, 'date': '2025-01-01', 'total_reactions': 1},
        {'id': 2, 'date': '2025-01-02', 'total_reactions': 2},
    ])

    assert len(_top_records(df, 10)) == 2


ENTITY_WITHOUT_USERNAME = SimpleNamespace(id=1006503122, username=None)
ENTITY_WITH_USERNAME = SimpleNamespace(id=1, username='chan')


@pytest.mark.parametrize(('target', 'expected'), [
    ('@durov', 'https://t.me/durov/42'),
    ('durov', 'https://t.me/durov/42'),
    ('https://t.me/durov', 'https://t.me/durov/42'),
    ('t.me/durov/999', 'https://t.me/durov/42'),
    ('https://t.me/durov?single', 'https://t.me/durov/42'),
    ('https://t.me/s/durov', 'https://t.me/durov/42'),
    ('https://t.me/s/durov/999', 'https://t.me/durov/42'),
])
def test_message_link_uses_public_slug_from_target(target, expected):
    assert _message_link(target, ENTITY_WITHOUT_USERNAME, 42) == expected


@pytest.mark.parametrize('target', [
    'https://t.me/c/1006503122/564',
    't.me/c/1006503122/564',
    'c/1006503122/564',
])
def test_message_link_keeps_private_channel_entity_id(target):
    assert _message_link(target, ENTITY_WITHOUT_USERNAME, 42) == 'https://t.me/c/1006503122/42'


def test_message_link_uses_entity_username_for_numeric_target():
    assert _message_link('1006503122', ENTITY_WITH_USERNAME, 42) == 'https://t.me/chan/42'


def test_message_link_falls_back_to_private_link_for_numeric_target():
    assert _message_link('1006503122', ENTITY_WITHOUT_USERNAME, 42) == 'https://t.me/c/1006503122/42'


def test_message_link_uses_entity_username_for_invite_link():
    assert _message_link('https://t.me/+abcdef', ENTITY_WITH_USERNAME, 42) == 'https://t.me/chan/42'


def test_message_link_falls_back_to_private_link_for_invite_link():
    assert _message_link('https://t.me/+abcdef', ENTITY_WITHOUT_USERNAME, 42) == 'https://t.me/c/1006503122/42'


def test_reaction_label_reads_standard_emoticon_without_network():
    client = FakeClient()

    label = asyncio.run(_reaction_label(client, SimpleNamespace(emoticon='👍'), {}))

    assert label == '👍'
    assert client.calls == 0


def test_reaction_label_maps_paid_reactions_to_star():
    client = FakeClient()

    label = asyncio.run(_reaction_label(client, ReactionPaid(), {}))

    assert label == '⭐'
    assert client.calls == 0


def test_reaction_label_resolves_and_caches_custom_emoji():
    docs = [SimpleNamespace(attributes=[SimpleNamespace(alt='🦞')])]
    client = FakeClient(docs=docs)
    cache = {}
    reaction = SimpleNamespace(document_id=5334575279731909928)

    first = asyncio.run(_reaction_label(client, reaction, cache))
    second = asyncio.run(_reaction_label(client, reaction, cache))

    assert first == '🦞'
    assert second == '🦞'
    assert client.calls == 1
    assert cache[5334575279731909928] == '🦞'


def test_reaction_label_falls_back_when_custom_emoji_lookup_fails():
    client = FakeClient(error=RuntimeError('lookup failed'))
    cache = {}
    reaction = SimpleNamespace(document_id=123)

    first = asyncio.run(_reaction_label(client, reaction, cache))
    second = asyncio.run(_reaction_label(client, reaction, cache))

    assert first == 'custom emoji 123'
    assert second == 'custom emoji 123'
    assert client.calls == 1


def test_reaction_label_falls_back_when_custom_emoji_document_is_empty():
    client = FakeClient(docs=[])
    reaction = SimpleNamespace(document_id=456)

    label = asyncio.run(_reaction_label(client, reaction, {}))

    assert label == 'custom emoji 456'


def test_reaction_label_falls_back_to_string_for_unknown_reaction():
    class UnknownReaction:
        def __str__(self):
            return 'unknown-reaction'

    client = FakeClient()

    label = asyncio.run(_reaction_label(client, UnknownReaction(), {}))

    assert label == 'unknown-reaction'
    assert client.calls == 0
