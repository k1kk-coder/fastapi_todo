from fastapi import HTTPException, status


def raise_item_not_found():
    raise HTTPException(
        status_code=404,
        detail="Item not found",
        headers={"X-Header-Error": "Nothing to be seen"}
    )


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception_response
