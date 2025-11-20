# /api/index.py

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi # NEW IMPORT

# Add path for helpers
sys.path.append(os.path.realpath('.'))

# Import helpers (we removed the downloader/transcriber imports)
from python_helpers.embed_text import embed_main as run_embedding_pipeline
from python_helpers.blog_generation import generate_blog_post
from python_helpers.rag import setup_pinecone_index, load_and_upsert_data, query_video

# --- Models ---
class VideoRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str

class BlogRequest(BaseModel):
    transcript_file: str

app = FastAPI()
pinecone_index = setup_pinecone_index()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to extract Video ID
def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

# --- API Endpoint 1: Process Video (New Lightweight Version) ---
@app.post("/api/process-video")
async def process_video(request: VideoRequest):
    try:
        print(f"Processing URL: {request.url}")
        video_id = get_video_id(request.url)
        
        if not video_id:
            raise Exception("Invalid YouTube URL")

        # 1. Fetch Transcript (No download needed!)
        print(f"Fetching transcript for {video_id}...")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # 2. Format it for your pipeline
        # We structure it exactly like the old Sarvam output so downstream code doesn't break
        formatted_entries = []
        for entry in transcript_list:
            formatted_entries.append({
                "transcript": entry['text'],
                "start_time_seconds": entry['start'],
                "end_time_seconds": entry['start'] + entry['duration'],
                "speaker_id": "Unknown" # Captions don't have speaker diarization
            })
            
        transcript_data = {
            "diarized_transcript": {
                "entries": formatted_entries
            }
        }

        # 3. Save to /tmp (Required for Vercel)
        import json
        transcript_file = f"/tmp/{video_id}_transcript.json"
        with open(transcript_file, "w") as f:
            json.dump(transcript_data, f)
            
        # 4. Embed (Using the new API-based embedder)
        # We pass the file path to your existing embed logic
        embedded_file = await run_embedding_pipeline(transcript_file)
        
        if not embedded_file:
            raise Exception("Embedding failed.")
            
        # 5. Upsert to Pinecone
        load_and_upsert_data(pinecone_index, embedded_file)
        
        print("Pipeline complete!")
        return {"status": "success", "transcript_file": transcript_file}

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# --- API Endpoint 2: Ask Question ---
@app.post("/api/ask-question")
async def ask_question(request: QueryRequest):
    try:
        answer_stream, contexts = query_video(pinecone_index, request.query)
        final_answer = "".join([chunk for chunk in answer_stream])
        return {"answer": final_answer, "contexts": contexts}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# --- API Endpoint 3: Generate Blog ---
@app.post("/api/generate-blog")
async def generate_blog(request: BlogRequest):
    try:
        blog_post_md = generate_blog_post(request.transcript_file)
        return {"blog_content": blog_post_md}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
