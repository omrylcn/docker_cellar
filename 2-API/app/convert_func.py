from skimage.io import imread,imsave
from skimage.color import rgb2gray
from skimage.transform import resize 
import os

def grey_image(input_path:str,output_path:str):
    #params=json.load(open("data/param/parameters.json","r"))

    #images = []
    for filename in os.listdir(input_path):
        path = os.path.join(input_path, filename)
        if os.path.isfile(path):
            
            #files.append(filename)
            grey_image=rgb2gray(imread(path))
            #print(output_path)
            output_file=filename.split(".")[0]+"_grey."+filename.split(".")[1]
            p=os.path.join(output_path,output_file)
            imsave(p,grey_image)
            



#convert_image(UPLOAD_DIRECTORY,DOWNLOAD_DIRECTORY)

