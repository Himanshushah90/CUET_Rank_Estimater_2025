from supabase import create_client
import os
import environ

env = environ.Env()
url = env('SUPABASE_URL')
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNkZW9wb3RucHV1cGlzd3h1Z2xjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDM0NTExMCwiZXhwIjoyMDY1OTIxMTEwfQ.sX0jfSRULcVEp7xJxScPi5v1oW8ad1gDRl-FiFMH-IA'
supabase = create_client(url, key)

def get_courses():
    response = supabase.table("courses").select("*").order("course_name").execute()
    return response.data or []

def get_subjects():
    response = supabase.table("subjects").select("*").order("subject_name").execute()
    return response.data or []

def get_combinations_for_course(course_id):
    response = supabase.table("course_combinations").select("*").eq("course_id", course_id).order("priority").execute()
    return response.data or []

def insert_submission(data):
    response = supabase.table("submissions").insert(data).execute()
    return response

def get_submission(unique_id):
    response = supabase.table("submissions").select("*").eq("unique_id", unique_id).execute()
    return response.data[0] if response.data else None

def get_all_submissions():
    response = supabase.table("submissions").select("*").execute()
    return response.data or []