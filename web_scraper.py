__author__ = "Amirreza Eskandarani"

import time
import requests
from urllib.request import urljoin
from bs4 import BeautifulSoup
from urllib.request import urlparse
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from tkinter import *

root = Tk()

# create a horizontal scrollbar by
# setting orient to horizontal
h = Scrollbar(root, orient = 'horizontal')

# attach Scrollbar to root window at
# the bootom
h.pack(side = BOTTOM, fill = X)

# create a vertical scrollbar-no need
# to write orient as it is by
# default vertical
v = Scrollbar(root)

# attach Scrollbar to root window on
# the side
v.pack(side = RIGHT, fill = Y)

# create a Text widget with 1920 chars
# width and 1080 lines height
# here xscrollcomannd is used to attach Text
# widget to the horizontal scrollbar
# here yscrollcomannd is used to attach Text
# widget to the vertical scrollbar
t = Text(root, width = 1920, height = 1080, wrap = NONE,
        xscrollcommand = h.set,
        yscrollcommand = v.set)
        


def download_link(link):
    content = requests.get(link).content
    name = link.replace("/", "").replace(":", "_")

    if (
        link.endswith("png")
        or link.endswith("jpg")
        or link.endswith("jpeg")
        or link.endswith("svg")
    ):
        with open(f"{name}.png", "wb") as image:
            image.write(content)

    elif link.endswith("gif"):
        with open(f"{name}.gif", "wb") as gif:
            gif.write(content)

    elif link.endswith("mp4"):
        with open(f"{name}.mp4", "wb") as video:
            video.write(content)

    else:
        with open(f"{name}.html", "wb") as html:
            html.write(content)


# https://www.geeksforgeeks.org/web-crawling-using-breadth-first-search-at-a-specified-depth/
def crawl(address, depth):

    # Set for storing urls with same domain
    links_intern = set()
    input_url = address
    # depth = 1

    # Set for storing urls with different domain
    links_extern = set()
    links_images = set()

    # Method for crawling a url at next level
    def level_crawler(input_url):
        temp_urls = set()
        current_url_domain = urlparse(input_url).netloc

        # Creates beautiful soup object to extract html tags
        beautiful_soup_object = BeautifulSoup(requests.get(input_url).content, "lxml")

        # Access all anchor tags from input
        # url page and divide them into internal
        # and external categories
        list = ["a", "img"]

        for anchor in beautiful_soup_object.findAll(list):
            href = anchor.attrs.get("href")
            image = anchor.attrs.get("src")

            if image != "" and image != None:
                image = urljoin(input_url, image)
                image_parsed = urlparse(image)
                image = image_parsed.scheme
                image += "://"
                image += image_parsed.netloc
                image += image_parsed.path
                final_parsed_img = urlparse(image)
                links_images.add(image)
                is_valid = bool(final_parsed_img.scheme) and bool(
                    final_parsed_img.netloc
                )

            elif href != "" and href != None:
                href = urljoin(input_url, href)
                href_parsed = urlparse(href)
                href = href_parsed.scheme
                href += "://"
                href += href_parsed.netloc
                href += href_parsed.path
                final_parsed_href = urlparse(href)
                is_valid = bool(final_parsed_href.scheme) and bool(
                    final_parsed_href.netloc
                )

                if is_valid:
                    if current_url_domain not in href and href not in links_extern:
                        links_extern.add(href)
                        # lbl=Label(window, text=href, fg='black', font=("Helvetica", 14))
                        # lbl.place(x=0+i, y=0+i)
                        # print("Extern - {}".format(href))
                    elif current_url_domain in href and href not in links_intern:
                       
                        t.insert(END,"Internal Links: " + str(href) + "\n")

                        # attach Text widget to root window at top
                        t.pack(side=TOP, fill=X)
                
                        # here command represents the method to
                        # be executed xview is executed on
                        # object 't' Here t may represent any
                        # widget
                        h.config(command=t.xview)
            
                        # here command represents the method to
                        # be executed yview is executed on
                        # object 't' Here t may represent any
                        # widget
                        v.config(command=t.yview)
                        links_intern.add(href)                        
                        # print("Intern - {}".format(href))
                        temp_urls.add(href)
        return temp_urls

    if depth == 0:
        print("Intern - {}".format(input_url))

    elif depth == 1:
        level_crawler(input_url)

    else:
        # We have used a BFS approach
        # considering the structure as
        # a tree. It uses a queue based
        # approach to traverse
        # links upto a particular depth.
        queue = []
        queue.append(input_url)
        for j in range(depth):
            for count in range(len(queue)):
                url = queue.pop(0)
                urls = level_crawler(url)
                for i in urls:
                    queue.append(i)

    return links_intern, links_images


if __name__ == "__main__":

    links, images = crawl("https://google.com/", 1)
    # multithread
    t1 = time.perf_counter()
    with ThreadPoolExecutor(20) as executor:
        executor.map(download_link, links.union(images))
    t2 = time.perf_counter()
    t.insert(END,"Multi Threaded Code Took : " + str(t2-t1) + " seconds")
    root.mainloop()
    # print(f"Multi Threaded Code Took :{t2 - t1} seconds")

# multi process
#     t1 = time.perf_counter()
#     with Pool(10) as executor:
#         executor.map(download_link, links)
#     t2 = time.perf_counter()
#     print(f'Multi process Code Took :{t2 - t1} seconds')
