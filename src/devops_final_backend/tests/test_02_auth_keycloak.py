""" Test 02: Keycloak Auth provider

Check that, for the test user, tokens can be generated and decoded
"""

import keycloak
import pytest
from fastapi import HTTPException

from devops_final_backend.services import auth
from devops_final_backend.settings import settings


def test_get_user_tokens_fail():
    with pytest.raises(keycloak.exceptions.KeycloakAuthenticationError):
        auth.get_user_tokens("user", "pass")

def test_get_current_user_fail():
    with pytest.raises(HTTPException):
        auth.get_current_user("invalid-token")

def test_auth_flow_ok():
    assert settings.keycloak_test_username is not None
    assert settings.keycloak_test_password is not None

    token = auth.get_user_tokens(settings.keycloak_test_username, settings.keycloak_test_password)
    auth.get_current_user(token["access_token"])