"""Admin auth/settings API regression tests: cookies, origins, validation, revision, persistence restore."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from pymongo import MongoClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
load_dotenv(ROOT / 'frontend' / '.env')
load_dotenv(ROOT / 'backend' / '.env')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
VALID_ORIGIN = BASE_URL
VALID_PROXY_ORIGIN = os.environ['CORS_ORIGINS'].split(',')[1].strip()
EVIL_ORIGIN = 'https://evil.example'


@pytest.fixture(scope='session')
def mongo_db():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    yield db
    client.close()


@pytest.fixture
def anon_client():
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    return session


@pytest.fixture(scope='module')
def admin_session(mongo_db):
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})

    login = session.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': ADMIN_PASSWORD},
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert login.status_code == 200, f'Admin login failed: {login.status_code} {login.text}'

    original = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert original.status_code == 200
    original_data = original.json()

    yield session, original_data

    latest = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    if latest.status_code == 401:
        refreshed = session.post(f'{BASE_URL}/api/admin/refresh', headers={'Origin': VALID_ORIGIN}, timeout=15)
        assert refreshed.status_code == 200
        latest = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert latest.status_code == 200

    latest_data = latest.json()
    if latest_data['settings'] != original_data['settings']:
        restore_payload = {**original_data['settings'], 'revision': latest_data['revision']}
        restored = session.put(
            f'{BASE_URL}/api/admin/settings',
            json=restore_payload,
            headers={'Origin': VALID_ORIGIN},
            timeout=15,
        )
        assert restored.status_code == 200


# Module: auth/session/cookie/origin behavior
def test_admin_password_hash_and_session_indexes_exist(mongo_db):
    admin = mongo_db.admin_users.find_one({'_id': 'admin'})
    assert admin is not None
    assert isinstance(admin.get('password_hash'), str)
    assert admin['password_hash'].startswith('$2b$')

    session_indexes = set(mongo_db.admin_sessions.index_information().keys())
    attempts_indexes = set(mongo_db.admin_login_attempts.index_information().keys())
    assert 'session_id_1' in session_indexes
    assert 'expires_at_1' in session_indexes
    assert 'expires_at_1' in attempts_indexes


def test_mutation_endpoints_reject_missing_and_evil_origin(anon_client):
    missing = anon_client.post(f'{BASE_URL}/api/admin/login', json={'password': ADMIN_PASSWORD}, timeout=15)
    evil = anon_client.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': ADMIN_PASSWORD},
        headers={'Origin': EVIL_ORIGIN},
        timeout=15,
    )
    assert missing.status_code == 403
    assert evil.status_code == 403


def test_login_accepts_known_explicit_origins_and_sets_secure_httponly_cookies(anon_client):
    direct = anon_client.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': ADMIN_PASSWORD},
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    via_proxy = anon_client.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': ADMIN_PASSWORD},
        headers={'Origin': VALID_PROXY_ORIGIN},
        timeout=15,
    )
    assert direct.status_code == 200
    assert via_proxy.status_code == 200
    assert direct.json() == {'authenticated': True}

    cookie_header = direct.headers.get('set-cookie', '').lower()
    assert 'access_token=' in cookie_header
    assert 'refresh_token=' in cookie_header
    assert 'httponly' in cookie_header
    assert 'secure' in cookie_header
    assert 'path=/api/admin' in cookie_header


def test_wrong_password_rejected_without_leaking_sensitive_data(anon_client):
    response = anon_client.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': 'WrongPassword!'},
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert response.status_code == 401
    body = response.text.lower()
    assert 'password_hash' not in body
    assert 'jwt_secret' not in body


def test_authenticated_reload_logout_and_replayed_cookie_rejected(admin_session):
    session, _ = admin_session

    me_before = session.get(f'{BASE_URL}/api/admin/me', timeout=15)
    assert me_before.status_code == 200

    snapshot = requests.cookies.RequestsCookieJar()
    for cookie in session.cookies:
        snapshot.set_cookie(cookie)

    logout = session.post(f'{BASE_URL}/api/admin/logout', headers={'Origin': VALID_ORIGIN}, timeout=15)
    assert logout.status_code == 200
    assert logout.json() == {'authenticated': False}

    me_after = session.get(f'{BASE_URL}/api/admin/me', timeout=15)
    assert me_after.status_code == 401

    replay = requests.Session()
    replay.headers.update({'Content-Type': 'application/json'})
    replay.cookies = snapshot
    replay_me = replay.get(f'{BASE_URL}/api/admin/me', timeout=15)
    assert replay_me.status_code == 401

    relogin = session.post(
        f'{BASE_URL}/api/admin/login',
        json={'password': ADMIN_PASSWORD},
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert relogin.status_code == 200


def test_refresh_works_when_access_cookie_missing_and_tampered_access_rejected(admin_session):
    session, _ = admin_session

    for cookie in list(session.cookies):
        if cookie.name == 'access_token':
            session.cookies.clear(cookie.domain, cookie.path, cookie.name)
    refresh = session.post(f'{BASE_URL}/api/admin/refresh', headers={'Origin': VALID_ORIGIN}, timeout=15)
    assert refresh.status_code == 200
    me = session.get(f'{BASE_URL}/api/admin/me', timeout=15)
    assert me.status_code == 200

    bad = requests.Session()
    bad.headers.update({'Content-Type': 'application/json'})
    bad.cookies.set('access_token', 'tampered.invalid.token', path='/api/admin', secure=True)
    rejected = bad.get(f'{BASE_URL}/api/admin/me', timeout=15)
    assert rejected.status_code == 401


# Module: settings CRUD/validation/concurrency/persistence
def test_settings_require_auth_and_hide_secrets(anon_client):
    no_auth = anon_client.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert no_auth.status_code == 401


def test_settings_put_persists_five_independent_fields_and_public_config_reflects(admin_session, mongo_db):
    session, original = admin_session
    current = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert current.status_code == 200
    data = current.json()

    payload = {
        'like_url': 'https://x.com/LastZhood/status/1111111111111111111',
        'repost_url': 'https://x.com/LastZhood/status/2222222222222222222',
        'reply_text': 'Türkçe satır 1\nSatır 2 özel karakter: çğışöü İĞŞ 🚀',
        'reply_url': 'https://x.com/LastZhood/status/3333333333333333333',
        'claim_text': 'CLAIM ON X metni — çok satırlı\nYeni satır ✅',
        'revision': data['revision'],
    }
    saved = session.put(
        f'{BASE_URL}/api/admin/settings',
        json=payload,
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert saved.status_code == 200
    saved_data = saved.json()
    assert saved_data['settings']['like_url'] == payload['like_url']
    assert saved_data['settings']['repost_url'] == payload['repost_url']
    assert saved_data['settings']['reply_text'] == payload['reply_text']
    assert saved_data['settings']['reply_url'] == payload['reply_url']
    assert saved_data['settings']['claim_text'] == payload['claim_text']

    persisted = mongo_db.campaign_settings.find_one({'_id': 'x-campaign'})
    assert persisted is not None
    assert persisted['settings']['like_url'] == payload['like_url']
    assert persisted['settings']['repost_url'] == payload['repost_url']
    assert persisted['settings']['reply_text'] == payload['reply_text']
    assert persisted['settings']['reply_url'] == payload['reply_url']
    assert persisted['settings']['claim_text'] == payload['claim_text']

    public = session.get(f'{BASE_URL}/api/config', timeout=15)
    assert public.status_code == 200
    config = public.json()
    like_task = next(item for item in config['tasks'] if item['id'] == 'like')
    repost_task = next(item for item in config['tasks'] if item['id'] == 'repost')
    assert like_task['url'] == payload['like_url']
    assert repost_task['url'] == payload['repost_url']
    assert config['comment_message'] == payload['reply_text']
    assert config['share_text'] == payload['claim_text']

    response_text = saved.text.lower()
    assert 'password_hash' not in response_text
    assert 'jwt_secret' not in response_text
    assert 'mongo_url' not in response_text

    # Put original back immediately for isolated assertion and keep final fixture restore as guard.
    rollback = session.put(
        f'{BASE_URL}/api/admin/settings',
        json={**original['settings'], 'revision': saved_data['revision']},
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert rollback.status_code == 200


def test_invalid_payload_rejected_and_db_unchanged(admin_session, mongo_db):
    session, _ = admin_session
    before = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert before.status_code == 200
    before_data = before.json()

    invalid = {
        'like_url': 'javascript:alert(1)',
        'repost_url': 'http://x.com/LastZhood/status/2',
        'reply_text': '   ',
        'reply_url': 'https://user:pass@x.com/LastZhood/status/3',
        'claim_text': '',
        'revision': before_data['revision'],
        'extra_field': 'not-allowed',
    }
    rejected = session.put(
        f'{BASE_URL}/api/admin/settings',
        json=invalid,
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert rejected.status_code == 422

    after = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert after.status_code == 200
    after_data = after.json()
    assert after_data['settings'] == before_data['settings']

    db_doc = mongo_db.campaign_settings.find_one({'_id': 'x-campaign'}, {'_id': 0, 'settings': 1})
    assert db_doc['settings'] == before_data['settings']


def test_stale_revision_returns_409_and_does_not_overwrite(admin_session):
    session, _ = admin_session
    start = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert start.status_code == 200
    current = start.json()

    first = session.put(
        f'{BASE_URL}/api/admin/settings',
        json={
            **current['settings'],
            'claim_text': f"{current['settings']['claim_text']} [{datetime.now(timezone.utc).isoformat()}]",
            'revision': current['revision'],
        },
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert first.status_code == 200

    stale = session.put(
        f'{BASE_URL}/api/admin/settings',
        json={
            **current['settings'],
            'claim_text': 'stale write should fail',
            'revision': current['revision'],
        },
        headers={'Origin': VALID_ORIGIN},
        timeout=15,
    )
    assert stale.status_code == 409


def test_put_with_evil_origin_denied_even_with_auth_cookie(admin_session):
    session, _ = admin_session
    current = session.get(f'{BASE_URL}/api/admin/settings', timeout=15)
    assert current.status_code == 200
    data = current.json()

    denied = session.put(
        f'{BASE_URL}/api/admin/settings',
        json={**data['settings'], 'revision': data['revision']},
        headers={'Origin': EVIL_ORIGIN},
        timeout=15,
    )
    assert denied.status_code == 403


def test_seed_campaign_no_overwrite_when_document_exists(monkeypatch):
    import campaign as cp

    class FakeCollection:
        def __init__(self):
            self.update_calls = 0

        async def find_one(self, query, projection):
            return {'revision': 3}

        async def update_one(self, query, update, upsert=False):
            self.update_calls += 1

    class FakeDB:
        def __init__(self):
            self.campaign_settings = FakeCollection()

    fake_db = FakeDB()
    monkeypatch.setattr(cp, 'environment_values', lambda: {
        'X_LIKE_LINK': 'https://x.com/env-like',
        'X_COMMENT_MESSAGE': 'ENV_TEXT',
        'X_SHARE_TEXT': 'ENV_SHARE',
    })

    import asyncio

    asyncio.run(cp.seed_campaign(fake_db))
    assert fake_db.campaign_settings.update_calls == 0


def test_login_throttle_after_five_failures_then_429_and_cleanup(anon_client, mongo_db):
    attempts_before = {doc['_id'] for doc in mongo_db.admin_login_attempts.find({}, {'_id': 1})}
    try:
        statuses = []
        for _ in range(6):
            response = anon_client.post(
                f'{BASE_URL}/api/admin/login',
                json={'password': 'totally-wrong-password'},
                headers={'Origin': VALID_ORIGIN},
                timeout=15,
            )
            statuses.append(response.status_code)
        assert statuses[:5] == [401, 401, 401, 401, 401]
        assert statuses[5] == 429
    finally:
        attempts_after = {doc['_id'] for doc in mongo_db.admin_login_attempts.find({}, {'_id': 1})}
        created = list(attempts_after - attempts_before)
        if created:
            mongo_db.admin_login_attempts.delete_many({'_id': {'$in': created}})


def test_seed_admin_updates_existing_admin_when_password_changes(monkeypatch):
    import admin_security as sec
    import bcrypt

    class FakeAdminUsers:
        def __init__(self):
            self.updates = 0
            self.existing_hash = bcrypt.hashpw(b'OriginalPass123', bcrypt.gensalt()).decode()

        async def find_one(self, query, projection):
            return {'password_hash': self.existing_hash}

        async def update_one(self, query, update, upsert=False):
            self.updates += 1

    class FakeCollection:
        async def create_index(self, *args, **kwargs):
            return None

        async def delete_many(self, *args, **kwargs):
            return None

    class FakeDB:
        def __init__(self):
            self.admin_sessions = FakeCollection()
            self.admin_login_attempts = FakeCollection()
            self.admin_users = FakeAdminUsers()

    db = FakeDB()
    monkeypatch.setenv('ADMIN_PASSWORD', 'DifferentPass123')
    monkeypatch.setenv('JWT_SECRET', 'x' * 64)

    import asyncio

    asyncio.run(sec.seed_admin(db))
    assert db.admin_users.updates == 1
