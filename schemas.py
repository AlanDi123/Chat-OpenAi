from pydantic import BaseModel
from typing import Literal, Optional

class WSRequest(BaseModel):
    prompt: str

class WSResponseText(BaseModel):
    role: Literal["assistant", "user"]
    content: str
    stream: Optional[bool] = False

class WSResponseImage(BaseModel):
    type: Literal["image"]
    url: str

class WSResponseError(BaseModel):
    type: Literal["error"]
    message: str
