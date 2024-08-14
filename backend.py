# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# # Define a model for the request body
# class Item(BaseModel):
#     name: str
#     price: float
#     is_available: bool

# @app.post("/")
# async def create_item(item: Item):
#     return {"name": item.name, "price": item.price, "is_available": item.is_available}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RSChatGPT_shell import RSChatGPT  # Make sure to import your RSChatGPT class
import os

app = FastAPI()

class QueryRequest(BaseModel):
    image_path: str
    question: str

# Initialize RSChatGPT here
load_dict = {
    "ImageCaptioning": "cpu",
    "SceneClassification": "cpu",
    "ObjectDetection": "cpu",
    "LandUseSegmentation": "cpu",
    "ObjectCounting": "cpu",
    "EdgeDetection": "cpu",
    "Conversation": "cpu"
}

bot = RSChatGPT(gpt_name="gpt-3.5-turbo", load_dict=load_dict, openai_key=None, proxy_url=None)
bot.initialize()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
@app.post("/ask/")
async def ask_gpt(query: QueryRequest):
    try:
        # Ensure the image path is valid
        if not os.path.exists(query.image_path):
            raise HTTPException(status_code=400, detail="Image path does not exist.")

        # Run the image query through RSChatGPT
        state = []
        state = bot.run_image(query.image_path, state, query.question)
        
        # Extract the response and observation from the state
        response = state[-1] if state else "No response generated."
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}




@app.post("/ask-fixed/")
async def ask_fixed():
    # Define fixed values
    fixed_image_path = "./image/airport_1_jpg.rf.3c38a93e805e111768dd2e37658c7c75.jpg" 
    fixed_question = "how many plane are in the image"

    # Ensure the image path is valid
    if not os.path.exists(fixed_image_path):
        raise HTTPException(status_code=400, detail="Image path does not exist.")

    try:
        # Run the image query through RSChatGPT
        state = []
        state,image_path = bot.run_image(fixed_image_path, state, fixed_question)
        
        # Extract the response and observation from the state
        response = state[-1] if state else "No response generated."

        return {
            "response": response,
            "result_image_path": image_path
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))