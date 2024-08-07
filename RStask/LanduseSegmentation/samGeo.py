import logging
import torch
import numpy as np
from PIL import Image
from skimage import io
from samgeo.text_sam import LangSAM

class SAMLandUseSegmentation:
    def __init__(self, device):
        self.device = device
        self.model = LangSAM()

    def inference(self, image_path, text_prompt, updated_image_path):  
        try:  
            # Perform segmentation using LangSAM  
            self.model.predict(image_path, text_prompt, box_threshold=0.24, text_threshold=0.24)  

            result_image = self.model.show_anns(  
                    cmap="BrBG",  
                    box_color="red",  
                    alpha=0.5,  
                    title=f"Automatic Segmentation of {text_prompt}",  
                    output=updated_image_path  
                )  

        except Exception as e:  
            print(f"Segmentation failed: {str(e)}. Please check if the text prompt is supported.")
        return text_prompt+' segmentation result in '+updated_image_path


if __name__ == '__main__':
    device = "cpu"  # Specify your device (e.g., "cuda" for GPU)
    net = SAMLandUseSegmentation(device)

    # Specify the local image path and text prompt
    image_path = "D:/fifthYear/5th_year_project/Remote-Sensing-ChatGPT-main/image/airport_2_jpg.rf.0c4836cd5c5d2fb278e52703808dbadc.jpg"  # Update this path to your local image
    text_prompt = "car"
    updated_image_path = "D:/fifthYear/5th_year_project/Remote-Sensing-ChatGPT-main/image/3.tif"

    # Run inference
    result = net.inference(image_path, text_prompt, updated_image_path)
    print(result)
