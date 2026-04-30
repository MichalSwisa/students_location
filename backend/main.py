import time
from urllib import response

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

def get_location_random():
    import random
    lat = 31.783 + random.uniform(-0.3, 0.3)
    lon = 35.216 + random.uniform(-0.3, 0.3)
    #random timestamp in the last half hour
    timestamp = int((time.time() - random.uniform(0, 1800)) * 1000)
    return {"ID": "123456789", "Coordinates": {"Latitude": {"Degrees": lat, "Minutes": "00", "Seconds": "00"}, "Longitude": {"Degrees": lon, "Minutes": "00", "Seconds": "00"}}, "Time": timestamp}


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

    
@app.get("/students")
def get_students(teacher_id: int | None = None, id: int  | None = None, full_name: str | None = None, class_id: str | None = None, all: bool | None = None):
    if id:
        return {"data": supabase.table("Users").select("*").eq("id", id).eq("role", "student").execute().data}
    elif full_name:
        return {"data": supabase.table("Users").select("*").eq("full_name", full_name).eq("role", "student").execute().data}
    elif class_id:
        return {"data": supabase.table("Users").select("*").eq("class_id", class_id).eq("role", "student").execute().data}
    elif teacher_id:
        temp_teacher = supabase.table("Users").select("*").eq("id", teacher_id).execute()
        if temp_teacher.data and len(temp_teacher.data) > 0:
            teacher = temp_teacher.data[0]
            return {"data": supabase.table("Users").select("*").eq("class_id", teacher["class_id"]).eq("role", "student").execute().data}
        else:
            return {"error": "Teacher not found or invalid teacher_id"}
    elif all:
        return {"data": supabase.table("Users").select("*").eq("role", "student").execute().data}
    else:
        return {}   
    


@app.get("/teachers")
def get_teachers(id: int | None = None, full_name: str | None = None, class_id: str | None = None):
    if id:
        return {"data": supabase.table("Users").select("*").eq("id", id).eq("role", "teacher").execute().data}
    elif full_name:
        return {"data": supabase.table("Users").select("*").eq("full_name", full_name).eq("role", "teacher").execute().data}
    elif class_id:
        return {"data": supabase.table("Users").select("*").eq("class_id", class_id).eq("role", "teacher").execute().data}
    else:
        return {"data": supabase.table("Users").select("*").eq("role", "teacher").execute().data}

    

@app.get("/user_by_id")
def get_user_by_id(id: int):
    user = supabase.table("Users").select("*").eq("id", id).execute()
    if user.data and len(user.data) > 0:
        return {"data": user.data[0]}
    else:
        return {"error": "User not found"}


@app.get("/all")
def get_all():
    return {"data": supabase.table("Users").select("*").execute().data}

        
@app.get("/login")
def get_all_login_data(id: int):
    person = supabase.table("Users").select("*").eq("id", id).execute()
    
    if person.data and len(person.data) > 0:
        return {"innerdata":person.data[0]}
    else:
        return {"error": "person not in system"}
    
@app.post("/activate_location")
def activate_location(id: int):
    try:
        location = get_location_random()

        response = supabase.table("Locations").insert({
            "id": id,
            "lat": location["Coordinates"]["Latitude"]["Degrees"],
            "lon": location["Coordinates"]["Longitude"]["Degrees"],
        }).execute()
        
        if not response.data:
            return {"error": "Failed to activate location"}
        
        return response.data[0]
    
    except Exception as e:
        return {"error": f"Error in activating location: {str(e)}"}
    
    
@app.post("/deactivate_location")
def deactivate_location(id: int):
    try:
        response = supabase.table("Locations").delete().eq("id", id).execute()
        
        if not response.data:
            return {"error": "Failed to deactivate location"}
        
        return response.data[0] 
    
    except Exception as e:
        return {"error": f"Error in deactivating location: {str(e)}"}
    
    
@app.get("/locations")
def get_locations(id: int | None = None):
    try:
        response = None
        if id:
            response = supabase.table("Locations").select("*").eq("id", id).execute()
        else:
            response = supabase.table("Locations").select("*").execute()
        
        if not response.data:
            return {"error": "Failed to get locations"}
        
        return {"data": response.data}
    
    except Exception as e:
        return {"error": f"Error in getting locations: {str(e)}"}
    

@app.get("/update_locations")
def update_location():
    try:
        response = get_locations()
        if "error" in response:
            return {"error": "Failed to update location"}
        for location in response["data"]:
            addto = (location["lat"] + location["lon"]) % 0.02 - 0.03
            if addto % 0.01 == 0:
                addto = -addto
            if location["lat"] + addto > 33.3 or location["lat"] + addto < 29.5 or location["lon"] + addto > 35.4 or location["lon"] + addto < 34.2:
                random_location = get_location_random()

                response3 = supabase.table("Locations").update({
                    "lat": random_location["Coordinates"]["Latitude"]["Degrees"],
                    "lon": random_location["Coordinates"]["Longitude"]["Degrees"]
                }).eq("id", location["id"]).execute()
                if not response3.data:
                    return {"error": "Failed to update location"}
            else:   
                response2 = supabase.table("Locations").update({
                    "lat": location["lat"] + addto,
                    "lon": location["lon"] + addto,
                    }).eq("id", location["id"]).execute()
                if not response2.data:
                    return {"error": "Failed to update location"}
        
        return {"message": "Success"} 
    
    except Exception as e:
        return {"error": f"Error in updating location: {str(e)}"}

