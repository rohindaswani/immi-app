def test_root_endpoint(client):
    """
    Test that the root endpoint returns a welcome message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Immigration Advisor API" in response.json()["message"]