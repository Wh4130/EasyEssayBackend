from pydantic import BaseModel
class Document(BaseModel):
    fileid: str
    filename: str
    content: str
    user_id: str
    tag: str 
    length: int
    lang: str
    additional_prompt: str
