import os

import re
import uuid
from skimage import io
import argparse
import inspect
from langchain.chat_models import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.agents.initialize import initialize_agent
from langchain.agents.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import numpy as np
from Prefix import  RS_CHATGPT_PREFIX, RS_CHATGPT_FORMAT_INSTRUCTIONS, RS_CHATGPT_SUFFIX
from RStask import ImageEdgeFunction,CaptionFunction,LanduseFunction,DetectionFunction,CountingFuncnction,SceneFunction,InstanceFunction
import base64  
from io import BytesIO  
from PIL import Image

os.makedirs('image', exist_ok=True)
def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func
    return decorator
def get_new_image_name(org_img_name, func_name="update"):
    head_tail = os.path.split(org_img_name)
    head = head_tail[0]
    tail = head_tail[1]
    name_split = tail.split('.')[0].split('_')
    this_new_uuid = str(uuid.uuid4())[:4]
    recent_prev_file_name = name_split[0]
    new_file_name = f'{this_new_uuid}_{func_name}_{recent_prev_file_name}.png'.replace('__','_')
    return os.path.join(head, new_file_name)


# Function to convert image to Base64  
def convert_image_to_base64(image_path):  
    # Load the image  
    image = io.imread(image_path)  

    # Convert the image array to a byte array  
    pil_image = Image.fromarray(image)  
    buffered = BytesIO()  
    pil_image.save(buffered, format="JPEG")  # or PNG, depending on your image type  

    # Encode the byte array to Base64  
    return base64.b64encode(buffered.getvalue()).decode('utf-8')  

class Conversation:
    def __init__(self, device):
        print(f"Initializing Conversation to {device}")
        self.device = device
        self.ollama = Ollama(base_url='http://172.25.1.139:11434', model="llava:latest")  # Initialize the Ollama Llava model

    @prompts(name="Image Conversation",
             description="Engage in a conversation about the image directly."
             " You can ask questions like 'What are the object categories in the image?'"
             " or 'Where are the buildings located?'. The input to this tool should be a string,"
             " representing the image_path.")
    def inference(self, image_path, question):
        # Convert the image to Base64
        image_b64 = convert_image_to_base64(image_path)

        # Bind the Base64 image data and invoke the model
        ollama_with_image = self.ollama.bind(images=[image_b64])  # Wrap in a list for multiple images
        response = ollama_with_image.invoke(question)

        return response

class EdgeDetection:
    def __init__(self, device):
        print("Initializing Edge Detection Function....")
        self.func = ImageEdgeFunction()
    @prompts(name="Edge Detection On Image",
             description="useful when you want to detect the edge of the remote sensing image. "
                         "like: detect the edges of this image, or canny detection on image, "
                         "or perform edge detection on this image, or detect the  edge of this image. "
                         "The input to this tool should be a string, representing the image_path")
    def inference(self, inputs):
        updated_image_path=get_new_image_name(inputs, func_name="edge")
        self.func.inference(inputs,updated_image_path)
        return updated_image_path

class ObjectCounting:
    def __init__(self, device):
        self.func=CountingFuncnction(device)
    @prompts(name="Count object",
             description="useful when you want to count the number of the  object in the image. "
                         "like: how many planes are there in the image? or count the number of bridges"
                         "The input to this tool should be a comma separated string of two, "
                         "representing the image_path, the text description of the object to be counted")
    def inference(self, inputs):
        image_path, det_prompt = inputs.split(",")
        det_prompt = det_prompt.lstrip() 
        log_text=self.func.inference(image_path,det_prompt)
        return log_text


# class InstanceSegmentation:
#     def __init__(self, device):
#         print("Initializing InstanceSegmentation")
#         self.func=InstanceFunction(device)
#     @prompts(name="Instance Segmentation for Remote Sensing Image",
#              description="useful when you want to apply man-made instance segmentation for the image. The expected input category include plane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, vehicle, helicopter, roundabout, soccer ball field, and swimming pool."
#                          "like: extract plane from this image, "
#                          "or predict the ship in this image, or extract tennis court from this image, segment harbor from this image, Extract the vehicle in the image. "
#                          "The input to this tool should be a comma separated string of two, "
#                          "representing the image_path, the text of the category,selected from plane, or ship, or storage tank, or baseball diamond, or tennis court, or basketball court, or ground track field, or harbor, or bridge, or vehicle, or helicopter, or roundabout, or soccer ball field, or  swimming pool. ")
#     def inference(self, inputs):
#         image_path, det_prompt = inputs.split(",")
#         updated_image_path = get_new_image_name(image_path, func_name="instance_" + det_prompt)
#         text=self.func.inference(image_path, det_prompt,updated_image_path)
#         return text

class SceneClassification:
    def __init__(self, device):
        print("Initializing SceneClassification")
        self.func=SceneFunction(device)
    @prompts(name="Scene Classification for Remote Sensing Image",
             description="useful when you want to know the type of scene or function for the image. "
                         "like: what is the category of this image?, "
                         "or classify the scene of this image, or predict the scene category of this image, or what is the function of this image. "
                         "The input to this tool should be a string, representing the image_path. ")
    def inference(self, inputs):
        output_txt=self.func.inference(inputs)
        return output_txt


class LandUseSegmentation:
    def __init__(self, device):
        print("Initializing LandUseSegmentation")
        self.func=LanduseFunction(device)

    @prompts(name="Segmentation for Remote Sensing Image",
             description="useful when you want to apply segmentation for the image"
                         "like: generate landuse map from this image, "
                         "or predict the landuse on this image, or extract building from this image, segment roads from this image, Extract the water bodies in the image. "
                         "The input to this tool should be a comma separated string of two, "
                         "representing the image_path, the text of the category selected to be segmented")
    def inference(self, inputs):
        image_path, det_prompt = inputs.split(",")
        updated_image_path = get_new_image_name(image_path, func_name="landuse")
        text=self.func.inference(image_path, det_prompt,updated_image_path)
        return text

class ObjectDetection:
    def __init__(self, device):
        self.func=DetectionFunction(device)


    @prompts(name="Detect the given object",
             description="useful when you only want to detect the bounding box of the certain objects in the picture according to the given text."
                         "like: detect the plane, or can you locate an object for me."
                         "The input to this tool should be a comma separated string of two, "
                         "representing the image_path, the text description of the object to be found")

    def inference(self, inputs):
        image_path, det_prompt = inputs.split(",")
        updated_image_path = get_new_image_name(image_path, func_name="detection_" + det_prompt.replace(' ', '_'))
        log_text=self.func.inference(image_path, det_prompt,updated_image_path)
        return log_text

class ImageCaptioning:
    def __init__(self, device):
        print(f"Initializing ImageCaptioning to {device}")
        self.device = device
        self.func=CaptionFunction(device)
    @prompts(name="Get Photo Description",
             description="useful when you want to know what is inside the photo. receives image_path as input. "
                         "The input to this tool should be a string, representing the image_path. ")
    def inference(self, image_path):
        captions = self.func.inference(image_path)
        print(f"\nProcessed ImageCaptioning, Input Image: {image_path}, Output Text: {captions}")
        return captions

class RSChatGPT:  
    def __init__(self, gpt_name, load_dict, openai_key, proxy_url):  
        print(f"Initializing RSChatGPT, load_dict={load_dict}")  
        if 'ImageCaptioning' not in load_dict:  
            raise ValueError("You have to load ImageCaptioning as a basic function for RSChatGPT")  
        self.models = {}  
        self.last_tool_name = None  # Track the last tool used  

        # Load Basic Foundation Models  
        for class_name, device in load_dict.items():  
            self.models[class_name] = globals()[class_name](device=device)  
        
        # Load Template Foundation Models  
        for class_name, module in globals().items():  
            if getattr(module, 'template_model', False):  
                template_required_names = {k for k in inspect.signature(module.__init__).parameters.keys() if k != 'self'}  
                loaded_names = set([type(e).__name__ for e in self.models.values()])  
                if template_required_names.issubset(loaded_names):
                    self.models[class_name] = globals()[class_name](
                        **{name: self.models[name] for name in template_required_names})
                    
        print(f"All the Available Functions: {self.models}")  

        self.tools = []  
        for instance in self.models.values():  
            for e in dir(instance):  
                if e.startswith('inference'):  
                    func = getattr(instance, e)  
                    self.tools.append(Tool(name=func.name, description=func.description, func=func))  

        # Add the new Conversation tool  
        self.models['Conversation'] = Conversation(device='cpu')  # Ensure the Conversation class is instantiated  
        self.tools.append(Tool(name="Image Conversation", description="Engage in a conversation about the image directly.", func=self.models['Conversation'].inference))  

        print("====================================================================================")  
        print("tools=", self.tools)  
        print("-------------------------------------------------------------------------------------")  
        self.llm = ChatOllama(model="llava:latest", temperature=0, base_url="http://172.25.1.139:11434")  
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)  

    def initialize(self):  
        self.memory.clear()  # clear previous history  
        PREFIX, FORMAT_INSTRUCTIONS, SUFFIX = RS_CHATGPT_PREFIX, RS_CHATGPT_FORMAT_INSTRUCTIONS, RS_CHATGPT_SUFFIX  
        self.agent = initialize_agent(  
            self.tools,  
            self.llm,  
            agent="conversational-react-description",  
            verbose=True,  
            memory=self.memory,  
            return_intermediate_steps=True,  
            stop=["\nObservation:", "\n\tObservation:","Observation:"],  
            agent_kwargs={'prefix': PREFIX, 'format_instructions': FORMAT_INSTRUCTIONS, 'suffix': SUFFIX},  
        )  
        print("======================================")  
        print("======================================")  
        print("==============Hellllo=================")  
        print("======================================")  
        print("======================================")            

    def stop_if_tool_used_twice(self, tool_name):  
        if tool_name == self.last_tool_name:  
            print("Stopping: Tool used twice in a row.")  
            return True  # Indicates we should stop the agent  
        self.last_tool_name = tool_name  
        return False  # Indicates we can continue  

    def run_text(self, text, state):  
        print("run_text=", text)  
        res = self.agent({"input": text.strip()})  

        tool_name = res.get('tool_name', None)  # Assuming the response contains the tool name  
        if self.stop_if_tool_used_twice(tool_name):  
            return state  # Early return to prevent further processing  

        print("_________QQQQQQQQ_______1___________QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        res['output'] = res['output'].replace("\\", "/")  
        print("_________QQQQQQQQ_______2___________QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        response = re.sub('(image/[-\w]*.png)', lambda m: f'![](file={m.group(0)})*{m.group(0)}*', res['output'])  
        print("_________QQQQQQQQ_______3___________QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        state = state + [(text, response)]  
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        print(f"\nProcessed run_text, Input text: {text}\nCurrent state: {state}\n"  
              f"Current Memory: {self.agent.memory.buffer}")  
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")  
        return state  
    
    def run_image(self, image_dir, state, txt=None):  
        image_filename = os.path.join('image', f"{str(uuid.uuid4())[:8]}.png")  
        print("image_filename=", image_filename)  
        img = io.imread(image_dir)  
        io.imsave(image_filename, img.astype(np.uint8))  
        description = self.models['ImageCaptioning'].inference(image_filename)  
        print("======================================")  
        print("======================================")  
        print("description=", description)  
        print("======================================")  
        print("======================================")  
        Human_prompt = f' Provide a remote sensing image named {image_filename}. The description is: {description}. This information helps you to understand this image, but you should use tools to finish following tasks, rather than directly imagine from my description and if you used the same action twice in a row then stop. If you understand, say "Received".'  
        AI_prompt = "Received."  
        self.memory.chat_memory.add_user_message(Human_prompt)  
        self.memory.chat_memory.add_ai_message(AI_prompt)  

        state = state + [(f"![](file={image_filename})*{image_filename}*", AI_prompt)]  
        print(f"\nProcessed run_image, Input image: {image_filename}\nCurrent state: {state}\n"  
              f"Current Memory: {self.agent.memory.buffer}")  
        state = self.run_text(f'{txt} {image_filename} ', state)  
        print("======================================")  
        print("======================================")  
        print("======================state=================", state)  
        print("======================================")  
        print("======================================")  
        return state  

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--openai_key', type=str,required=False)
    parser.add_argument('--image_dir', type=str,required=True)
    parser.add_argument('--gpt_name', type=str, default="gpt-3.5-turbo",choices=['gpt-3.5-turbo-1106','gpt-3.5-turbo','gpt-4','gpt-4-0125-preview','gpt-4-turbo-preview','gpt-4-1106-preview'])
    parser.add_argument('--proxy_url', type=str, default=None)
    parser.add_argument('--load', type=str,help='Image Captioning is basic models that is required. You can select from [ImageCaptioning,ObjectDetection,LandUseSegmentation,ObjectCounting,SceneClassification,EdgeDetection,Conversation]',
                        default="ImageCaptioning_cpu,SceneClassification_cpu,ObjectDetection_cpu,LandUseSegmentation_cpu,ObjectCounting_cpu,EdgeDetection_cpu,Conversation_cpu ")
    args = parser.parse_args()
    state = []
    load_dict = {e.split('_')[0].strip(): e.split('_')[1].strip() for e in args.load.split(',')}
    bot = RSChatGPT(gpt_name=args.gpt_name,load_dict=load_dict,openai_key=args.openai_key,proxy_url=args.proxy_url)
    bot.initialize()
    print('RSChatGPT initialization done, you can now chat with RSChatGPT~')
    bot.initialize()
    txt='detect the planes in the image'
    state=bot.run_image(args.image_dir, [], txt)

    while 1:
        txt = input('You can now input your question.(e.g. Extract buildings from the image)\n')
        state = bot.run_image(args.image_dir, state, txt)


