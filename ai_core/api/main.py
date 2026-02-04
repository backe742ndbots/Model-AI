# import uvicorn
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional, Dict, Any

# #original logic
# from ai_core.tools.query_router import handle_user_query


# # --- 1. Define Data Models (The Contract) ---
# # This ensures the frontend sends exactly what we expect.
# class QueryRequest(BaseModel):
#     text: str
#     session_id: Optional[str] = "default"
#     user_id: Optional[str] = "guest"

# class QueryResponse(BaseModel):
#     status: str
#     reply_text: str
#     data: Optional[Dict[str, Any]] = None

# # --- 2. Initialize App ---
# app = FastAPI(
#     title="Property AI API",
#     description="Voice-enabled AI Property Management System",
#     version="1.0.0"
# )

# # --- 3. CORS Policy (Crucial for Frontend) ---
# # This allows your localhost frontend to talk to this backend.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, change this to your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- 4. Health Check (The Heartbeat) ---
# @app.get("/health")
# async def health_check():
#     """Checks if the server is running."""
#     return {"status": "ok", "service": "property-ai-core"}

# # --- 5. The Main Query Endpoint ---
# @app.post("/query", response_model=QueryResponse)
# async def process_query(request: QueryRequest):
#     """
#     Receives user text, sends it to AI (Simulated for now), 
#     and returns the response.
#     """
#     print(f"🔹 Received Query: {request.text}")

#     # TODO: Connect this to Person 1's logic later.
#     # For now, we simulate a response so you can build the Frontend.
    
#     # Mock Logic:
#     # fake_ai_reply = f"I received your request: '{request.text}'. The AI logic is currently being connected."
    
#     # return QueryResponse(
#     #     status="success",
#     #     reply_text=fake_ai_reply,
#     #     data=None
#     # )
    
#     #original reply
    
    
    
    
    
# try:
#     result = handle_user_query(request.text, limit=5)

#     if result["result_count"] == 0:
#         reply = (
#             "I couldn’t find any exact matches for your request. "
#             "Would you like to broaden the criteria?"
#         )
#     else:
#         reply = (
#             f"I found {result['result_count']} matching properties. "
#             f"Here are some good options."
#         )
    
#     return QueryResponse(
#         status="success",
#         reply_text=reply,
#         data=result
#     )      

    

# except Exception as e:
#     raise HTTPException(status_code=500, detail=str(e))
    
    
    
    

# # --- 6. Entry Point ---
# if __name__ == "__main__":
#     # Runs the server on port 8000
#     uvicorn.run("ai_core.api.main:app", host="0.0.0.0", port=8000, reload=True)




import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ai_core.tools.query_router import handle_user_query


# --- 1. Define Data Models ---
class QueryRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = "guest"


class QueryResponse(BaseModel):
    status: str
    reply_text: str
    data: Optional[Dict[str, Any]] = None


# --- 2. Initialize App ---
app = FastAPI(
    title="Property AI API",
    description="Voice-enabled AI Property Management System",
    version="1.0.0"
)


# --- 3. CORS Policy ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 4. Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "property-ai-core"}


# --- 5. Main Query Endpoint ---
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Receives user text, routes it to AI logic,
    and returns the response.
    """
    print(f"🔹 Received Query: {request.text}")

    try:
        result = handle_user_query(request.text, limit=5)

        if result["result_count"] == 0:
            reply = (
                "I couldn’t find any exact matches for your request. "
                "Would you like to broaden the criteria?"
            )
        else:
            reply = (
                f"I found {result['result_count']} matching properties. "
                "Here are some good options."
            )

        return QueryResponse(
            status="success",
            reply_text=reply,
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 6. Entry Point ---
if __name__ == "__main__":
    uvicorn.run(
        "ai_core.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
