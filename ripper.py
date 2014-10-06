#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
ripper.py

:Authors:
Soufian Salim (soufi@nsal.im)

:Date:
October 2nd, 2014

:Description:
Ubuntu documentation ripper
"""

from bs4 import BeautifulSoup
from hashlib import md5
from progressbar import ProgressBar
from utility import timed_print
from urlparse import urlparse

import os
import requests
import time
import urllib


domain = "doc.ubuntu-fr.org"
alternate = "_export/xhtml"
scheme = "http"
port = 80

import_folder = "import"
item_list_file = "list"


# Main
def main():
    progress_bar = ProgressBar()

    item_list = [
        item.strip() for item in open(item_list_file, "r").readlines() 
        if not item.startswith("#")
    ]

    timed_print("starting import of {0} items from '{1}'".format(len(item_list), domain))

    for item in progress_bar(item_list):
        item_url = "{0}://{1}:{2}/{3}/{4}".format(
            scheme, domain, port, alternate, item
        )

        local_path = "./{0}/{1}.html".format(import_folder, item)

        soup = request_soup(item_url, delay=3)

        if soup.find(id="cette_page_n_existe_pas_encore"):
            continue # the item's web page does not exist

        downloaded_urls = []

        for image in soup.findAll("img"):
            image_url = build_image_url(image["src"])

            if image_url in downloaded_urls:
                continue # already downloaded
            
            downloaded_urls.append(image_url)

            image_hash = md5_hash(image_url)

            image["src"] = "image_{0}".format(image_hash)
            image_path = "{0}/{1}".format(os.path.dirname(local_path), image["src"])

            download_file(image_url, image_path, delay=3)

        write_soup(soup, local_path)


def md5_hash(string):
    return md5(string.encode("utf-8")).hexdigest()


def build_image_url(tag):
    source = urlparse(tag)

    path = source.path[1:] if source.path.startswith("/") else source.path

    if source.query:
        path += "?" + source.query

    return "{0}://{1}:{2}/{3}".format(scheme, domain, port, path)


def write_soup(soup, path):
    """
    Writes an html document from a soup
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "w") as out:
        out.write(str(soup))


def request_soup(url, delay=0):
    """
    Returns a soup built from the page found at the requested url
    """
    time.sleep(delay)

    return BeautifulSoup(requests.get(url).text)


def download_file(url, path, delay=0):
    """
    Downloads a remote file
    """
    time.sleep(delay)

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    urllib.urlretrieve(url, path)


# Launch
if __name__ == "__main__":
    main()
