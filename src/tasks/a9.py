# import numpy as np
# from pathlib import Path
# from fastapi import HTTPException
# from src.utils.security import validate_path
# import requests
# import os

# AI_PROXY_BASE = os.getenv("AI_PROXY_BASE", "https://aiproxy.sanand.workers.dev/openai/v1")
# AIPROXY_TOKEN = os.environ.get('AIPROXY_TOKEN')

# def cosine_similarity(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# def get_embedding(text):
#     headers = {
#         "Authorization": f"Bearer {AIPROXY_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "input": text,
#         "model": "text-embedding-3-small"
#     }
#     response = requests.post(
#         f"{AI_PROXY_BASE}/embeddings",
#         headers=headers,
#         json=payload
#     )
#     if response.status_code != 200:
#         raise HTTPException(500, "Embedding API error")
#     return response.json()['data'][0]['embedding']

# def handle_a9(params):
#     try:
#         # Validate file paths
#         input_path = validate_path(params['input_file'])
#         output_path = validate_path(params['output_file'])
        
#         # Read comments
#         with open(input_path, 'r') as f:
#             comments = [line.strip() for line in f.readlines() if line.strip()]
            
#         if len(comments) < 2:
#             raise HTTPException(400, "Need at least 2 comments for comparison")
            
#         # Get embeddings
#         embeddings = [get_embedding(comment) for comment in comments]
        
#         # Find most similar pair
#         max_sim = -1
#         best_pair = (comments[0], comments[1])
        
#         for i in range(len(comments)):
#             for j in range(i+1, len(comments)):
#                 sim = cosine_similarity(embeddings[i], embeddings[j])
#                 if sim > max_sim:
#                     max_sim = sim
#                     best_pair = (comments[i], comments[j])
        
#         # Write result
#         with open(output_path, 'w') as f:
#             f.write('\n'.join(best_pair))
            
#         return {"status": "success", "similarity": float(max_sim)}
        
#     except Exception as e:
#         raise HTTPException(500, f"Processing failed: {str(e)}")

from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path
from src.utils.llm import AI_PROXY_BASE, AIPROXY_TOKEN
import numpy as np
import requests
import logging
import os

logger = logging.getLogger(__name__)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def handle_a9(params: dict):
    try:
        # Validate and resolve paths
        input_path = validate_path(params.get('input_file', '/data/comments.txt'))
        output_path = validate_path(params.get('output_file', '/data/comments-similar.txt'))
        
        # Verify input file exists
        if not input_path.exists():
            raise HTTPException(404, "Input file not found")
            
        # Read comments
        with open(input_path, 'r') as f:
            comments = [line.strip() for line in f if line.strip()]
            
        if len(comments) < 2:
            raise HTTPException(400, "At least two comments required")
            
        # Get embeddings in batch
        response = requests.post(
            f"{AI_PROXY_BASE}/embeddings",
            headers={
                "Authorization": f"Bearer {AIPROXY_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "input": comments,
                "model": "text-embedding-3-small"
            },
            timeout=20
        )
        
        # Handle API errors
        if response.status_code != 200:
            raise HTTPException(502, f"Embedding API error: {response.text}")
            
        embeddings = [item['embedding'] for item in response.json()['data']]
        
        # Find most similar pair
        max_sim = -1
        best_pair = None
        
        for i in range(len(comments)):
            for j in range(i+1, len(comments)):
                sim = cosine_similarity(embeddings[i], embeddings[j])
                if sim > max_sim:
                    max_sim = sim
                    best_pair = (comments[i], comments[j])
        
        # Write output
        with open(output_path, 'w') as f:
            f.write('\n'.join(best_pair))
            
        return {"status": "success", "similarity": float(max_sim)}
        
    except HTTPException as he:
        raise he
    except requests.exceptions.RequestException as e:
        logger.error(f"Embedding API connection failed: {str(e)}")
        raise HTTPException(504, "Embedding service unavailable")
    except Exception as e:
        logger.error(f"A9 processing failed: {str(e)}")
        raise HTTPException(500, f"Comment similarity analysis failed: {str(e)}")
