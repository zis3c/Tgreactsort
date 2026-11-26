import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

import sort_reactions
from sort_reactions import main

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def runner():
    return CliRunner()


def payload(result):
    return json.loads(result.stdout.strip())


def clear_credentials(monkeypatch):
    monkeypatch.delenv('API_ID', raising=False)
    monkeypatch.delenv('API_HASH', raising=False)


def test_json_requires_channel(runner):
    result = runner.invoke(main, ['--json'])

    assert result.exit_code == 1
    assert payload(result) == {
        'ok': False,
        'error': 'Provide --channel or --channels when using --json.',
    }


def test_json_rejects_watch_mode(runner):
    result = runner.invoke(main, ['--json', '--channel', '@chan', '--watch'])

    assert result.exit_code == 1
    assert payload(result) == {
        'ok': False,
        'error': '--watch cannot be combined with --json.',
    }


def test_json_missing_credentials_reports_error_without_prompt(monkeypatch, runner, tmp_path):
    clear_credentials(monkeypatch)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(main, ['--json', '--channel', '@chan'])

    assert result.exit_code == 1
    assert payload(result)['error'].startswith('Telegram API credentials missing')
    assert 'Enter your API ID' not in result.stdout


def test_json_batch_channels_does_not_prompt_for_channel(monkeypatch, runner, tmp_path):
    clear_credentials(monkeypatch)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(main, ['--json', '--channels', '@a', '--channels', '@b'])

    assert result.exit_code == 1
    assert payload(result)['error'].startswith('Telegram API credentials missing')
    assert 'Target Channel' not in result.stdout


def test_json_missing_session_reports_error(monkeypatch, runner, tmp_path):
    monkeypatch.setenv('API_ID', '12345')
    monkeypatch.setenv('API_HASH', 'abc')
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(main, ['--json', '--channel', '@chan'])

    assert result.exit_code == 1
    assert 'No authorized Telegram session' in payload(result)['error']


def test_json_success_aggregates_batch_results(monkeypatch, runner):
    monkeypatch.setenv('API_ID', '12345')
    monkeypatch.setenv('API_HASH', 'abc')
    calls = []

    async def fake_run_sort(*args, **kwargs):
        calls.append((args[2], kwargs))
        return {
            'ok': True,
            'channel': args[2],
            'total': 1,
            'csv': 'data/x.csv',
            'top': [],
        }

    def fake_asyncio_run(coro):
        if coro.cr_code.co_name == 'session_authorized':
            coro.close()
            return True
        try:
            coro.send(None)
        except StopIteration as stop:
            return stop.value

    monkeypatch.setattr(sort_reactions, 'run_sort', fake_run_sort)
    monkeypatch.setattr(sort_reactions.asyncio, 'run', fake_asyncio_run)

    result = runner.invoke(main, ['--json', '--channels', '@a', '--channels', '@b'])

    assert result.exit_code == 0
    assert payload(result)['ok'] is True
    assert [item['channel'] for item in payload(result)['results']] == ['@a', '@b']
    assert [call[0] for call in calls] == ['@a', '@b']


def test_json_failure_result_sets_nonzero_exit(monkeypatch, runner):
    monkeypatch.setenv('API_ID', '12345')
    monkeypatch.setenv('API_HASH', 'abc')

    async def fake_run_sort(*args, **kwargs):
        return {'ok': False, 'channel': args[2], 'error': 'boom'}

    def fake_asyncio_run(coro):
        if coro.cr_code.co_name == 'session_authorized':
            coro.close()
            return True
        try:
            coro.send(None)
        except StopIteration as stop:
            return stop.value

    monkeypatch.setattr(sort_reactions, 'run_sort', fake_run_sort)
    monkeypatch.setattr(sort_reactions.asyncio, 'run', fake_asyncio_run)

    result = runner.invoke(main, ['--json', '--channel', '@chan'])

    assert result.exit_code == 1
    assert payload(result)['ok'] is False
    assert payload(result)['results'][0]['error'] == 'boom'


def test_script_entrypoint_reports_unknown_option_as_json():
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'sort_reactions.py'), '--json', '--unknown-option'],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert proc.returncode == 1
    assert json.loads(proc.stdout.strip())['ok'] is False
    assert 'No such option' in json.loads(proc.stdout.strip())['error']
