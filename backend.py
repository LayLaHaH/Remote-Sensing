from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RSChat_shell import RSChat 
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
import ast
app = FastAPI()

class QueryRequest(BaseModel):
    image_path: str
    question: str

# Initialize RSChat here
load_dict = {
    "ImageCaptioning": "cpu",
    "SceneClassification": "cpu",
    "ObjectDetection": "cpu",
    "LandUseSegmentation": "cpu",
    "ObjectCounting": "cpu",
    "EdgeDetection": "cpu",
    "Conversation": "cpu"
}

bot = RSChat(load_dict=load_dict)
bot.initialize()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Serve static files from the "image" directory
app.mount("/images", StaticFiles(directory="C:/Users/Layla/Desktop/Remote-Sensing-ChatGPT-main/image"), name="images")

@app.post("/ask/")
async def ask(image_path: str = Form(...),question: str = Form(...)):
    try:
        # Ensure the image path is valid
        if not os.path.exists(image_path):
            raise HTTPException(status_code=400, detail="Image path does not exist.")

        # Extract the image name from the path
        image_name = os.path.basename(image_path)

        # Combine the new base path with the image name
        new_image_path = os.path.join('./image', image_name)

        # Run the image query through RSChat
        state = []
        state, observation = bot.run_image(new_image_path, state, question)

        if isinstance(observation, tuple):
            description, img_path = observation  # Directly unpack the tuple
            img_name = os.path.basename(img_path)
        else:
            raise ValueError("Observation is not in the expected tuple format.")
        # Extract the response and observation from the state
        response = state[-1] if state else "No response generated."
        
        return {
            "response": description,
            "result_image_path": f"images/{img_name}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

