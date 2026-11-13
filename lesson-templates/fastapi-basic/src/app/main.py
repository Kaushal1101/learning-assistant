from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Sandbox", version="0.1.0")


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class EchoResponse(BaseModel):
    echoed: str
    length: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str = "World") -> dict[str, str]:
    return {"message": f"Hello, {name}!"}


@app.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(echoed=payload.message, length=len(payload.message))
