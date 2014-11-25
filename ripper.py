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
from optparse import OptionParser
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

# Main
def main(options, arguments):
    items_file = arguments[0]
    import_folder = arguments[1]

    items = [
        item.strip() for item in open(items_file, "r").readlines() 
        if not item.startswith("#")
    ]

    timed_print("starting import of {0} items from '{1}'".format(len(items), domain))

    for item in items:
        item_url = "{0}://{1}:{2}/{3}/{4}".format(
            scheme, domain, port, alternate, item
        )

        timed_print("{0}/{1}: {2}".format(
            items.index(item) + 1, len(items), item)
        )

        local_path = "./{0}/{1}.html".format(import_folder, item)

        soup = request_soup(item_url, delay=options.delay)

        if soup.find(id="cette_page_n_existe_pas_encore"):
            continue # the item's web page does not exist

        downloaded_urls = []

        if options.images:
            images = soup.findAll("img")

            for image in images:
                timed_print("- image {0}/{1}: {2}".format(
                    images.index(image) + 1, len(images), image["src"])
                )

                image_url = build_image_url(image["src"])

                if image_url in downloaded_urls:
                    continue # already downloaded
                
                downloaded_urls.append(image_url)

                image_hash = md5_hash(image_url)

                image["src"] = "image_{0}".format(image_hash)
                image_path = "{0}/{1}".format(os.path.dirname(local_path), image["src"])

                download_file(image_url, image_path, delay=options.delay)

        write_soup(soup, local_path)


def md5_hash(string):
    """
    Returns the md5 hash of a string
    """
    return md5(string.encode("utf-8")).hexdigest()


def build_image_url(tag):
    """
    Builds the full url of an image from its tag attributes
    """
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
    op = OptionParser(usage="usage: %prog [options] item_file output_directory")

    op.add_option("-d", "--delay",
        dest="delay",
        type="int",
        default=3,
        help="delay between each request (defaults to 3)")

    op.add_option("--images",
        dest="images",
        default=False,
        action="store_true",
        help="check this flag if you want download images found in the documentation")

    options, arguments = op.parse_args()

    if len(arguments) != 2:
        op.error("this script takes exactly two arguments: \"item_file\" and \"output_directory\"")

    main(options, arguments)
