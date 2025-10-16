from fastapi.testclient import TestClient
from app.main import app
import uuid


def auth_headers(client: TestClient):
    # Register a fresh user to ensure bcrypt-hashed password
    unique = str(uuid.uuid4())[:8]
    email = f"test_{unique}@example.com"
    username = f"user_{unique}"
    password = "Passw0rd!"
    r = client.post('/api/v1/auth/register', data={
        'email': email,
        'username': username,
        'password': password
    })
    assert r.status_code == 200, r.text
    # Login
    r = client.post('/api/v1/auth/login', data={'username': email, 'password': password})
    assert r.status_code == 200, r.text
    token = r.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_learning_session_flow():
    # Use context manager to trigger startup (creates tables)
    with TestClient(app) as client:
        headers = auth_headers(client)

        # start
        r = client.post('/api/v1/learning/sessions/start', json={'role':'explainer','task_type':'Task 2'}, headers=headers)
        assert r.status_code == 200, r.text
        data = r.json()
        session_id = data['session']['id']
        assert 'first_prompt' in data

        # step with reply and delta
        r = client.post(f'/api/v1/learning/sessions/{session_id}/step', json={'user_input':'My thesis ...','draft_delta':'Intro paragraph draft'}, headers=headers)
        assert r.status_code == 200, r.text
        step = r.json()
        assert step['turn']['agent_output']

        # get session
        r = client.get(f'/api/v1/learning/sessions/{session_id}', headers=headers)
        assert r.status_code == 200
        sess = r.json()
        assert sess['latest_draft']['version'] >= 1

        # list sessions
        r = client.get('/api/v1/learning/sessions/', headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json().get('sessions', []), list)

        # list drafts
        r = client.get(f'/api/v1/learning/sessions/{session_id}/drafts', headers=headers)
        assert r.status_code == 200
        drafts = r.json().get('drafts', [])
        assert len(drafts) >= 1


