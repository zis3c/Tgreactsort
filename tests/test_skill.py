import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_skill():
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    assert text.startswith('---\n')
    _, frontmatter, body = text.split('---', 2)
    return yaml.safe_load(frontmatter), body


def test_skill_frontmatter_is_cross_agent_safe():
    meta, _ = load_skill()

    assert set(meta) == {'name', 'description'}
    assert meta['name'] == 'telegram-reactions-sorter'
    assert re.fullmatch(r'[a-z0-9-]+', meta['name'])
    assert len(meta['description']) >= 80
    assert 'Use when' in meta['description']


def test_skill_body_documents_setup_and_json_contract():
    _, body = load_skill()

    assert 'my.telegram.org' in body
    assert '--json' in body
    assert 'session_name.session' in body
    assert 'python sort_reactions.py --channel "@durov"' in body


@pytest.mark.parametrize('path', [
    'sort_reactions.py',
    'requirements.txt',
    '.env.example',
    'web/view_results.html',
    'web/app.js',
    'web/styles.css',
    'LICENSE',
    'README.md',
])
def test_skill_runtime_files_exist(path):
    assert (ROOT / path).is_file()


def test_env_example_uses_placeholders_not_real_credentials():
    text = (ROOT / '.env.example').read_text(encoding='utf-8')

    assert 'API_ID=your_api_id_here' in text
    assert 'API_HASH=your_api_hash_here' in text
