# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel
# from typing import Optional
#
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# class User(BaseModel):
#     login: str
#     email: Optional[str] = None
#     username: Optional[str] = None
#     is_expert: Optional[bool] = False
#     is_devops: Optional[bool] = False
#     disabled: Optional[bool] = False
#     app_settings: Optional[dict] = None
#
#
# class UserInDB(User):
#     hashed_password: str
#
#
# def get_user(db, login: str):
#     if login in db:
#         user_dict = db[login]
#         return UserInDB(**user_dict)
#
#
# def get_db():
#     users = get_collection_items(collection_name="users",
#                                  table_name="streamlit_users",
#                                  verbose=True)
#     db = {}
#     for idx, user in enumerate(users):
#         user.pop("_id")
#         user["hashed_password"] = f"fakehashed{idx}"
#         user["disabled"] = False
#         db[user["login"]] = user
#     return db
#
#
# def fake_hash_password(password: str):
#     return "fakehashed" + password
#
#
# def fake_decode_token(token):
#     users_db = get_db()
#     user = get_user(users_db, token)
#     return user
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user
#
#
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user