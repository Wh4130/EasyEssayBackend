from pydantic import BaseModel
class Document(BaseModel):
    fileid: str
    filename: str
    content: str
    user_id: str
    tag: str 
    lang: str
    additional_prompt: str
    db_url: str

class Message(BaseModel):
    query: str
    fileid: str
    param_k: int

class TestDB(BaseModel):
    gs_url: str
    fileid: str
    filename: str
    content: str
