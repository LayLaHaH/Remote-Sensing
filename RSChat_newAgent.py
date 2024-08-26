import os

import re
import uuid
from skimage import io
import argparse
import inspect
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.agents.initialize import initialize_agent
from langchain.agents.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import numpy as np
from Prefix import  RS_CHAT_PREFIX, RS_CHAT_FORMAT_INSTRUCTIONS, RS_CHAT_SUFFIX
from RStask import ImageEdgeFunction,CaptionFunction,LanduseFunction,DetectionFunction,CountingFuncnction,SceneFunction
import base64  
from io import BytesIO  
from PIL import Image

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate


# Define your custom prompt template
template = '''
Remote Sensing Chat is designed to assist with a wide range of remote sensing image related tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of remote sensing applications. Remote Sensing Chat is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Remote Sensing Chat can process and understand large amounts of  remote sensing images, knowledge, and text. As a expertized language model, Remote Sensing Chat can not directly read remote sensing images, but it has a list of tools to finish different remote sensing tasks. Each input remote sensing image will have a file name formed as "image/xxx.png", and Remote Sensing Chat can invoke different tools to indirectly understand the remote sensing image. When talking about images, Remote Sensing Chat is very strict to the file name and will never fabricate nonexistent files. When using tools to generate new image files, Remote Sesning Chat is also known that the image may not be the same as the user's demand, and will use other visual question answering tools or description tools to observe the real image. Remote Sensing Chat is able to use tools in a sequence, and is loyal to the tool observation outputs rather than faking the image content and image file name. It will remember to provide the file name from the last tool observation, if a new image is generated.

Human may provide new remote sensing images to Remote Sensing Chat with a description. The description helps Remote Sensing Chat to understand this image, but Remote Sensing Chat should use tools to finish following tasks, rather than directly imagine from the description.

Overall, Remote Sensing Chat is a powerful visual dialogue assistant tool that can help with a wide range of remote sensing tasks and provide valuable insights and information on a wide range of remote sensing applicatinos. 


You are tasked with answering the following questions to the best of your ability. You have access to the following tools:

{tools}

Use the following format for your responses:

Question: The input question you must answer
Thought: Always consider what action to take next
Action: The action to take, which should be one of [{tool_names}]
Action Input: The input for the action
Observation: The result of the action
... (this Thought/Action/Action Input/Observation can repeat as needed)
Thought: I now know the final answer
Final Answer: The final answer to the original input question

You are very strict to the filename correctness and will never fake
 a file name if it does not exist.
You will remember to provide the image file name loyally if it's provided in the last tool observation.

Begin!

Previous conversation history:
{chat_history}

New input: {input}
Since Remote Sensing Chat is a text language model, Remote Sensing Chat must use tools to observe 
remote sensing images rather than imagination.
The thoughts and observations are only visible for Remote Sensing Chat,
 Remote Sensing Chat should remember to repeat important information in the final response for Human. 
Thought: Do I need to use a tool? {agent_scratchpad} Let's think step by step.
'''

# Create the prompt template
prompt = PromptTemplate.from_template(template)


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
        return "",updated_image_path

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
        updated_image_path = get_new_image_name(image_path, func_name="counting_" + det_prompt.replace(' ', '_'))
        log_text,updated_image_path=self.func.inference(image_path, det_prompt,updated_image_path)
        return log_text,updated_image_path

class SceneClassification:
    def __init__(self, device):
        print("Initializing SceneClassification")
        self.func=SceneFunction(device)
    @prompts(name="Scene Classification for Remote Sensing Image",
             description="useful when you want to know the type of scene or function for the image. "
                         "like: what is the category of this image?, "
                         "or classify the scene of this image, or predict the scene category of this image, or what is the function of this image. "
                         "The input to this tool is just the image path , dont add anything after the image path ")
    def inference(self, inputs):
        output_txt=self.func.inference(inputs)
        return output_txt,None

class LandUseSegmentation:
    def __init__(self, device):
        print("Initializing LandUseSegmentation")
        self.func=LanduseFunction(device)

    @prompts(name="Land Use Segmentation for Remote Sensing Image",
             description="useful when you want to apply land use gegmentation for the image. The expected input category include Building, Road, Water, Barren, Forest, Farmland, Landuse."
                         "like: generate landuse map from this image, "
                         "or predict the landuse on this image, or extract building from this image, segment roads from this image, Extract the water bodies in the image. "
                         "The input to this tool should be a comma separated string of two, "
                         "representing the image_path, the text of the category,selected from Lnad Use, or Building, or Road, or Water, or Barren, or Forest, or Farmland, or Landuse.")
    def inference(self, inputs):
        image_path, det_prompt = inputs.split(",")
        updated_image_path = get_new_image_name(image_path, func_name="landuse")
        text,updated_image_path=self.func.inference(image_path, det_prompt,updated_image_path)
        return text,updated_image_path

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
        log_text,updated_image_path=self.func.inference(image_path, det_prompt,updated_image_path)
        return log_text,updated_image_path

class ImageCaptioning:
    def __init__(self, device):
        print(f"Initializing ImageCaptioning to {device}")
        self.device = device
        self.func=CaptionFunction(device)
    @prompts(name="Get Photo Description",
             description="useful when you want to know what is the caption of the photo. receives image_path as input. "
                         "The input to this tool should be a string, representing the image_path. ")
    def inference(self, image_path):
        captions = self.func.inference(image_path)
        print(f"\nProcessed ImageCaptioning, Input Image: {image_path}, Output Text: {captions}")
        return captions,image_path

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
             description="useful when you want to engage in  in a conversation with the image."
             " You can ask questions related to the content of the image "
             "like: What are the object categories in the image?"
             " or Where are the buildings located?, or give me the tags of the objects in the image"
             "The input to this tool must be a comma separated string of two, "
             "representing the image_path, the asked question , dont add the image path and the question together without the comma")

    def inference(self,inputs):
        image_path, question = inputs.split(",")
        # Convert the image to Base64
        image_b64 = convert_image_to_base64(image_path)

        # Bind the Base64 image data and invoke the model
        ollama_with_image = self.ollama.bind(images=[image_b64])  # Wrap in a list for multiple images
        response = ollama_with_image.invoke(question)

        return response,image_path

class RSChat:
    def __init__(self,load_dict):
        print(f"Initializing RSChatGPT, load_dict={load_dict}")
        if 'ImageCaptioning' not in load_dict:
            raise ValueError("You have to load ImageCaptioning as a basic function for RSChatGPT")
        self.models = {}
        # Load Basic Foundation Models
        for class_name, device in load_dict.items():
            self.models[class_name] = globals()[class_name](device=device)
        # Load Template Foundation Models
        for class_name, module in globals().items():
            if getattr(module, 'template_model', False):
                template_required_names = {k for k in inspect.signature(module.__init__).parameters.keys() if
                                           k != 'self'}
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
        self.models['Conversation'] = Conversation(device='cpu')  # Instantiate the Conversation class
        self.tools.append(Tool(name=self.models['Conversation'].inference.name, 
                                description=self.models['Conversation'].inference.description, 
                                func=self.models['Conversation'].inference))

        # self.llm = ChatOllama(model="llava:latest", temperature=0, base_url="http://localhost:11434")
        # self.llm = ChatOllama(model="llava:latest", temperature=0, base_url="http://172.25.1.139:11434")
        self.llm = ChatOllama(model="llava:latest", temperature=0, base_url="http://172.25.1.139:11434")

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)# return_messages=True

    def initialize(self):
        self.memory.clear() #clear previous history
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, handle_parsing_errors=True)  # Handle parsing errors

        print("======================================")
        print("===================Hellllo====================")
        print("======================================")
           

    def run_text(self, text, state):
        print("run_text=", text)
        res = self.agent_executor.invoke({"input": text.strip()})
        
        # Extract Observation and Thought from the response
        # observation = res.get('intermediate_steps', [])[-1][0].log if res.get('intermediate_steps') else "No Observation"
        if res.get('intermediate_steps'):
            # Assuming the last entry contains the observation
            last_step = res['intermediate_steps'][-1]
            observation = last_step[1]  # This should give you the desired observation value
        else:
            observation = "No Observation"

        res['output'] = res['output'].replace("\\", "/")
        response = re.sub('(image/[-\w]*.png)', lambda m: f'![](file={m.group(0)})*{m.group(0)}*', res['output'])
        state = state + [(text, response)]
        # print(f"\nProcessed run_text, Input text: {text}\nCurrent state: {state}\n"
        #       f"Current Memory: {self.agent.memory.buffer}")
        
        return state,observation
    def run_image(self, image_dir, state, txt=None):
        image_filename = os.path.join('image', f"{str(uuid.uuid4())[:8]}.png")
        # print("image_filename=",image_filename)
        img = io.imread(image_dir)
        io.imsave(image_filename, img.astype(np.uint8))
        description = self.models['ImageCaptioning'].inference(image_filename)
        Human_prompt = f' Provide a remote sensing image named {image_filename}. The description is: {description}. This information helps you to understand this image, but you should use tools to finish following tasks, rather than directly imagine from my description. If you understand, say \"Received\".'
        AI_prompt = "Received."
        self.memory.chat_memory.add_user_message(Human_prompt)
        self.memory.chat_memory.add_ai_message(AI_prompt)

        state = state + [(f"![](file={image_filename})*{image_filename}*", AI_prompt)]  
        # print(f"\nProcessed run_image, Input image: {image_filename}\nCurrent state: {state}\n"
        #       f"Current Memory: {self.agent.memory.buffer}")
        state,observation=self.run_text(f'{txt} {image_filename} ', state)
        print("==================state====================")
        print(state)
        print("======================================")
        return state,observation



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', type=str,required=True,default="./image/airport_2_jpg.rf.9b6c37c3675f890ca191797e3f36c015.jpg")
    parser.add_argument('--load', type=str,help='Image Captioning is basic models that is required. You can select from [ImageCaptioning,ObjectDetection,LandUseSegmentation,ObjectCounting,SceneClassification,EdgeDetection,Conversation]',
                        default="ImageCaptioning_cpu,SceneClassification_cpu,ObjectDetection_cpu,LandUseSegmentation_cpu,ObjectCounting_cpu,EdgeDetection_cpu,Conversation_cpu")
    args = parser.parse_args()
    state = []
    load_dict = {e.split('_')[0].strip(): e.split('_')[1].strip() for e in args.load.split(',')}
    bot = RSChat(load_dict=load_dict)
    bot.initialize()
    print('RSChat initialization done, you can now chat with RSChat~')
    bot.initialize()
    txt='give me the tags of the objects in the image'
    state,observation=bot.run_image(args.image_dir, [], txt)

    while 1:
        txt = input('You can now input your question.(e.g. Extract buildings from the image)\n')
        state,observation = bot.run_image(args.image_dir, state, txt)


