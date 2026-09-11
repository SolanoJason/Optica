from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer

password_hasher = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")