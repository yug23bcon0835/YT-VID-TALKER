import asyncio
import json
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# --- Configuration ---
# We use the same model you used locally to ensure vector compatibility
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize Client
# We use the environment variable HF_TOKEN
client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ.get("HF_TOKEN"),
)

async def embed(texts: list[str]) -> list[list[float]]:
    """
    Embeds text using Hugging Face InferenceClient (Serverless).
    """
    if not os.environ.get("HF_TOKEN"):
        print("❌ Error: HF_TOKEN not found. Cannot generate embeddings.")
        return []

    # Define a blocking function to run in a thread
    def _make_request():
        # feature_extraction returns the embeddings (vectors)
        return client.feature_extraction(texts, model=MODEL_ID)

    try:
        # Run synchronous client in a thread to avoid blocking FastAPI
        response = await asyncio.to_thread(_make_request)
        
        # The client might return a numpy array or list depending on installed packages.
        # Ensure we return a standard list of lists.
        if hasattr(response, 'tolist'):
            return response.tolist()
        return response

    except Exception as e:
        print(f"HF API Error: {e}")
        return []

async def embed_transcript(transcript: dict) -> dict:
    entries = transcript["diarized_transcript"]["entries"]
    
    # Process in batches to respect API payload limits
    batch_size = 50
    all_embeddings = []
    
    print(f"Starting embedding for {len(entries)} segments...")
    
    for i in range(0, len(entries), batch_size):
        batch_texts = [e["transcript"] for e in entries[i:i+batch_size]]
        print(f"Embedding batch {i} to {i+batch_size}...")
        
        batch_embeddings = await embed(batch_texts)
        
        if not batch_embeddings:
            print("⚠️ Warning: Batch returned empty embeddings.")
            # Fallback: fill with zeros to prevent crash, or handle error
            batch_embeddings = [[0.0] * 384 for _ in batch_texts]
            
        all_embeddings.extend(batch_embeddings)
    
    # Assign back to entries
    if len(all_embeddings) == len(entries):
        for i, emb in enumerate(all_embeddings):
            transcript["diarized_transcript"]["entries"][i]["embedding"] = emb
    else:
        print(f"❌ Mismatch! Entries: {len(entries)}, Embeddings: {len(all_embeddings)}")
        
    return transcript

async def embed_main(transcript_filepath: str) -> str | None:
    if not transcript_filepath:
        return None  
    
    # Save output to /tmp for Vercel compatibility
    output_filepath = transcript_filepath.replace(".json", "_embedded.json")
    
    try:
        with open(transcript_filepath, "r") as f:
            transcript = json.load(f)
            
        transcript = await embed_transcript(transcript)
        
        with open(output_filepath, "w") as f:
            json.dump(transcript, f)
            
        print(f"Saved embedded file to {output_filepath}")
        return output_filepath
    except Exception as e:
        print(f"Embedding process failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(embed_main("test_transcript.json"))
