from fastapi import FastAPI

app = FastAPI()

@appi.get("/health")
def health():
    return {"status": "ok"}