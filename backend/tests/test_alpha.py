def test_user_signup(client):
    response = client.post('/auth/signup', json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 201

def test_user_login(client):
    client.post('/auth/signup', json={
        "username": "newuser",
        "password": "password123"
    })
    response = client.post('/auth/login', json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_user_profile(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    profile_response = client.get('/auth/profile', headers=headers)
    print("RESPONSE JSON:", profile_response.json)
    assert profile_response.status_code == 200
    assert isinstance(profile_response.json, dict)

def test_user_coin(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "coin": 10000
    }

    coin_response = client.put('/auth/', json=data,headers=headers)

    print("RESPONSE JSON:", coin_response.json)
    assert coin_response.status_code == 200
    assert isinstance(coin_response.json, dict)

    assert "coin" in coin_response.json
    assert data["coin"] == 10000

    