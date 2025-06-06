
def test_get_acc(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    get_acc_response = client.get('/acc/',headers=headers)
    assert get_acc_response.status_code == 200
    assert isinstance(get_acc_response.json, list)

def test_create_acc(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
            "hero": 100,
            "skin": 100,
            "price": 200000,
            "description": "Empty",
            "rank": "Unrank",
    }
    create_acc_response = client.post('/acc/',json=data, headers=headers)
    assert create_acc_response.status_code == 201
    assert "acc_id" in create_acc_response.json

def test_details_acc(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    data = {
            "hero": 100,
            "skin": 100,
            "price": 200000,
            "description": "Empty",
            "rank": "Unrank",
    }
    create_acc_response = client.post('/acc/',json=data, headers=headers)
    assert create_acc_response.status_code == 201
    assert "acc_id" in create_acc_response.json
    acc_id = create_acc_response.json['acc_id']

    detals_acc_response = client.get(f'/acc/{acc_id}',headers=headers)
    assert detals_acc_response.status_code == 200
    assert isinstance(detals_acc_response.json, dict)

def test_delete_acc(authenticated_client):
    client, access_token = authenticated_client  # unpack

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
            "hero": 100,
            "skin": 100,
            "price": 200000,
            "description": "Empty",
            "rank": "Unrank",
    }
    create_acc_response = client.post('/acc/',json=data, headers=headers)
    assert create_acc_response.status_code == 201
    assert "acc_id" in create_acc_response.json
    acc_id = create_acc_response.json['acc_id']
    
    delete_acc_response = client.delete(f'/acc/{acc_id}',headers=headers)
    assert delete_acc_response.status_code == 200
    assert delete_acc_response.json["msg"] == "Mua acc thành công"