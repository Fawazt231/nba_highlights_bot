from supabase import create_client

from config import SUPABASE_API_URL, SUPABASE_ANON_PUBLIC_API_KEY

url = SUPABASE_API_URL
key = SUPABASE_ANON_PUBLIC_API_KEY
supabase = create_client(url, key)

def already_uploaded(clip_id):
    result = supabase.table("uploaded_clips").select("clip_id").eq("clip_id", clip_id).execute()
    return len(result.data) > 0

def mark_as_uploaded(clip_id, title):
    supabase.table("uploaded_clips").insert({"clip_id": clip_id, "title": title}).execute()
    print(f"Successfully uploaded \"{title}\" with post_id, {clip_id}, to supabase Table")
