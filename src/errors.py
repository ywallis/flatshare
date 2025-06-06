from fastapi.exceptions import HTTPException


unauthorized_error = HTTPException(status_code=401, detail="Unauthorized")
