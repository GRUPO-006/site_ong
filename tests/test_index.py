def test_index_success(client):
    response = client.get('/')

    assert response.status_code == 200


def test_contato_success(client):
    response = client.get('/contato')

    assert response.status_code == 200


def test_blog_success(client):
    response = client.get('/blog')

    assert response.status_code == 200
