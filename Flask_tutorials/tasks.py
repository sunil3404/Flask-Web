from app import app
from app import r, q
import time
from bs4 import BeautifulSoup as bsp
import requests
import time , os
from PIL import Image

def background_task(n):
    delay = 2
    print("Task Running")
    print(f"simulate a delay {delay}")
    time.sleep(delay)

    print(len(n))
    print("Task is complete")

    return len(n)

def count_words(url):
    page = requests.get(url)
    page_soup = bsp(page.text, 'lxml')

    p_tags = " ".join([p.text for p in page_soup.find_all('p')])
    word_counter = {}
    for word in p_tags.split():
        if word not in word_counter:
            word_counter[word] = 1
        else:
            word_counter[word] += 1
    print(word_counter)
    print(f"Total words :  {len(word_counter)}")
    return word_counter

def image_task(image_dir, image_name):
    
    start_time = time.time()

    thumb = 30, 30
    small = 540, 540
    medium = 768, 768
    large = 1080, 1080
    xl = 1200, 1200


    image = Image.open(os.path.join(image_dir, image_name))
    image_ext = image_name.split(".")[-1]
    image_name = image_name.split(".")[0]

    ### Thumbnail ###
    thumbnail_image = image.copy()
    thumbnail_image.thumbnail(thumb,Image.LANCZOS)
    thumbnail_image.save(f"{os.path.join(image_dir, image_name)}-thumbnail.{image_ext}", optimize=True, quality=95)
    
    ###SMALL##
    small_image = image.copy()
    smaill_image.thumbnail(thumb,Image.LANCZOS)
    small_image.save(f"{os.path.join(image_dir, image_name)}-540.{image_ext}", optimize=True, quality=95)
    
    ###MEDIUM##
    medium_image = image.copy()
    medium_image.thumbnail(thumb,Image.LANCZOS)
    meidum_image.save(f"{os.path.join(image_dir, image_name)}-768.{image_ext}", optimize=True, quality=95)
    
    ###large##
    large_image = image.copy()
    large_image.thumbnail(thumb,Image.LANCZOS)
    large_image.save(f"{os.path.join(image_dir, image_name)}-1080.{image_ext}", optimize=True, quality=95)
    
    ###XL##
    xl= image.copy()
    xl_image.thumbnail(thumb,Image.LANCZOS)
    xl_image.save(f"{os.path.join(image_dir, image_name)}-1200.{image_ext}", optimize=True, quality=95)

    end = time.time()

    print(f"Task completed in {end-start}")

    return True


