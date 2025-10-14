from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID

from devops_final_backend.settings import settings

keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak_url,
    realm_name=settings.keycloak_realm,
    client_id=settings.keycloak_client_id,
    client_secret_key=settings.keycloak_client_secret,
)

oauth2_scheme = OAuth2PasswordBearer(
    description="Keycloak Direct Access Auth Provider for Client Services Authentification",
    tokenUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
    refreshUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate incoming auht tokens against keycloak auth provider

    Raises:
        HTTPException: 401 if keycloack does not recognize token or the user info does not contain a subject id

    Returns:
        dict: user info dictionary
    """

    try:
        user_info = keycloak_openid.introspect(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    if not user_info.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user info")

    return user_info
