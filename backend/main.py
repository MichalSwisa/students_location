
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from sympy import re
from pydantic import BaseModel


load_dotenv()  

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing VITE_SUPABASE_URL or VITE_SUPABASE_KEY in environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class Student(BaseModel):
    id: str | None = None
    full_name: str
    class_id: str


class Teacher(BaseModel):
    id: str | None = None
    full_name: str
    class_id: str


def get_supabase_client():
    global supabase
    if supabase: return supabase
    
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing VITE_SUPABASE_URL or VITE_SUPABASE_KEY")
    
    supabase = create_client(url, key)
    return supabase


@app.post("/students")
def add_student(student: Student):
    try:
        response = supabase.table("Users").insert({
            "id": student.id,
            "full_name": student.full_name,
            "class_id": student.class_id,
            "role": "student"
        }).execute()
        
        if not response.data:
            return {"error": "Failed to add student"}
        
        return response.data[0]
    
    except Exception as e:
        return {"error": f"Error in adding student: {str(e)}"}
    
    
@app.post("/teachers")
def add_teacher(teacher: Teacher):
    try:
        response = supabase.table("Users").insert({
            "id": teacher.id,
            "full_name": teacher.full_name,
            "class_id": teacher.class_id,
            "role": "teacher"
        }).execute()
        
        if not response.data:
            return {"error": "Failed to add teacher"}
        
        return response.data[0]
    
    except Exception as e:
        return {"error": f"Error in adding teacher: {str(e)}"}
    

@app.post("/teachers")
def add_teacher(teacher: Teacher):
    try:
        response = supabase.table("Users").insert({
            "id": teacher.id,
            "full_name": teacher.full_name,
            "class_id": teacher.class_id,
            "role": "teacher"
        }).execute()
        
        if not response.data:
            return {"error": "Failed to add teacher"}
        
        return response.data[0]
    
    except Exception as e:
        return {"error": f"Error in adding teacher: {str(e)}"}
    
    
@app.get("/students")
def get_students(teacher_id: int, id: int | None = None, full_name: str | None = None, class_id: str | None = None, all: bool | None = None):
    temp_teacher = supabase.table("Users").select("*").eq("id", teacher_id).execute()  #verify that a teacher asking
    if temp_teacher.data and len(temp_teacher.data) > 0:
        teacher = temp_teacher.data[0]
        if id:
            return {"data": supabase.table("Users").select("*").eq("id", id).eq("role", "student").execute().data}
        elif full_name:
            return {"data": supabase.table("Users").select("*").eq("full_name", full_name).eq("role", "student").execute().data}
        elif class_id:
            return {"data": supabase.table("Users").select("*").eq("class_id", class_id).eq("role", "student").execute().data}
        elif teacher_id:
            return {"data": supabase.table("Users").select("*").eq("class_id", teacher["class_id"]).eq("role", "student").execute().data}
        elif all:
            return {"data": supabase.table("Users").select("*").eq("role", "student").execute().data}
    else:
        return {"error": "Teacher not found or invalid teacher_id"}


@app.get("/teachers")
def get_teachers(teacher_id: int, id: int | None = None, full_name: str | None = None, class_id: str | None = None):
    temp_teacher = supabase.table("Users").select("*").eq("id", teacher_id).execute()  #verify that a teacher asking
    if temp_teacher.data and len(temp_teacher.data) > 0:
        if id:
            return {"data": supabase.table("Users").select("*").eq("id", id).eq("role", "teacher").execute().data}
        elif full_name:
            return {"data": supabase.table("Users").select("*").eq("full_name", full_name).eq("role", "teacher").execute().data}
        elif class_id:
            return {"data": supabase.table("Users").select("*").eq("class_id", class_id).eq("role", "teacher").execute().data}
        else:
            return {"data": supabase.table("Users").select("*").eq("role", "teacher").execute().data}
    else:
        return {"error": "Teacher not found or invalid teacher_id"}


@app.get("/all")
def get_all(teacher_id: int):
    temp_teacher = supabase.table("Users").select("*").eq("id", teacher_id).execute()  #verify that a teacher asking
    if temp_teacher.data and len(temp_teacher.data) > 0:
        return {"data": supabase.table("Users").select("*").execute().data}
    else:
        return {"error": "Teacher not found or invalid teacher_id"}

        
@app.get("/login")
def get_all_login_data(id: int):
    person = supabase.table("Users").select("*").eq("id", id).execute()
    
    if person.data and len(person.data) > 0:
        return {"innerdata":person.data[0]}
    else:
        return {"error": "person not in system"}
