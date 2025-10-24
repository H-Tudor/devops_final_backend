"""Test 02: Keycloak Auth provider

Check that, for the test user, tokens can be generated and decoded,
This requires keycloak to be Available or set the 'disable_api_testing` env var to True
to skip over these checks
"""

import keycloak
import pytest
from fastapi import HTTPException

from devops_final_backend.services import auth
from devops_final_backend.settings import settings


def test_get_user_tokens_fail():
    """Check that keycloak rejects invalid user / pass values"""
    if settings.disable_api_testing:
        return

    with pytest.raises(keycloak.exceptions.KeycloakAuthenticationError):
        auth.get_user_tokens("user", "pass")


def test_get_current_user_fail():
    """Check that keycloak rejects invalid tokens"""
    if settings.disable_api_testing:
        return

    with pytest.raises(HTTPException):
        auth.get_current_user("invalid-token")


def test_auth_flow_ok():
    """For a valid set of user / pass ensure tokens can be obtained and validated"""
    if settings.disable_api_testing:
        return

    assert settings.keycloak_test_username is not None
    assert settings.keycloak_test_password is not None

    token = auth.get_user_tokens(settings.keycloak_test_username, settings.keycloak_test_password)
    auth.get_current_user(token["access_token"])
