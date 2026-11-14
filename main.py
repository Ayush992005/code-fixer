from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from repair import repair
from run_code import run_code

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class Req(BaseModel):
    code: str
    language: str          # python | java | c | cpp
    max_attempts: int = 6


class RunReq(BaseModel):
    code: str
    language: str          # python | java | c | cpp
    stdin: str = ""        # optional text typed into the program


@app.post("/fix")
def fix(req: Req):
    return repair(req.code, req.language, req.max_attempts)


@app.post("/run")
def run(req: RunReq):
    if req.language not in ("python", "java", "c", "cpp"):
        raise HTTPException(status_code=400, detail="language must be python, java, c or cpp")
    return run_code(req.code, req.language, req.stdin)
