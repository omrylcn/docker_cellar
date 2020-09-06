# For  uploading image to convert to grey image
import requests

# load image
ii=open("test_image_old.jpg","rb").read()

# Upload image with post method
url= "http://127.0.0.1:5000/upload/test_image_old.jpg"
requests.post(url,data=ii)

# Convert image get request
convert= False
if convert == True:
    
    url= "http://127.0.0.1:5000/convert"
    requests.get(url)

