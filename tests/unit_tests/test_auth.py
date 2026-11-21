from src.services.tokens import TokenService


def test_create_access_token():
    data = {"user_id": 1}
    jwt_token = TokenService().create_access_token(data=data)

    assert isinstance(jwt_token, str)
