from src.services.tokens import TokenService


def test_create_access_token():
    data = {"user_id": 1}
    jwt_token = TokenService().create_access_token(data=data)

    payload = TokenService().decode_token(jwt_token)

    assert payload["user_id"] == data["user_id"]
