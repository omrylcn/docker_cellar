from skimage.io import imread,imsave
from skimage.color import rgb2gray
from skimage.transform import resize 
import json


params=json.load(open("data/param/parameters.json","r"))

image=imread(params["input_directory"])

grey_image=rgb2gray(image)

imsave(params["output_directory"],grey_image)

