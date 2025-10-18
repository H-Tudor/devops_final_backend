""" Test 10: API Testing using Schemathesis

Schemathesis is a powerful api testing tool that interprets the openapi.json
schema of an API then generates limit-tests to check that the code correctly
implements the declared schema.

This functionaliy does not replace unit tests, but is instead an integration test,
and it also tests the integration with the Keycloak auth provider thus a configured
and available Keycloak instance with a test user set is required
"""

from fastapi.testclient import TestClient
from schemathesis import AuthContext, AuthProvider, Case, openapi

from devops_final_backend.api import app
from devops_final_backend.services import auth
from devops_final_backend.settings import settings

schema = openapi.from_asgi("/openapi.json", app)


@schema.auth()
class AppAuth(AuthProvider):
    """Implementation of Schemathesis AuthProvider Protocol for preparing the required api token

    Args:
        AuthProvider (Protocol): Implemented Interface
    """

    def get(self, _case: Case, _ctx: AuthContext) -> str | None:
        """Obtain authentication data for the test case. (_case and _ctx are not required for the present flow)"""

        return (
            auth.get_user_tokens(settings.keycloak_test_username, settings.keycloak_test_password)["access_token"]
            if settings.keycloak_test_username and settings.keycloak_test_password
            else None
        )

    def set(self, case: Case, data: str, _ctx: AuthContext) -> None:
        """Apply authentication data to the test case. (_ctx is not required for the present flow)

        Args:
            case: Test case to modify.
            data: Authentication data from the `get` method.
        """

        case.headers["Authorization"] = f"Bearer {data}"


@schema.parametrize()
def test_api(case: Case):
    """Handler for each generated test case generated

    Args:
        case (Case): the case being tested
    """

    with TestClient(app) as client:
        case.call_and_validate(session=client)
