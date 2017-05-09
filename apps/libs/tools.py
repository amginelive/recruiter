from string import ascii_lowercase, digits
from random import randint, choice
from django.core.files.storage import default_storage
from easy_thumbnails.files import get_thumbnailer
import re


# generate random string
def random_string_gen(min_length, max_length):
    characters = ascii_lowercase + digits
    return "".join(choice(characters) for x in range(randint(min_length, max_length)))


# generate random filename (without checking if it's unique)
def filename_gen(file_ext):
    characters = ascii_lowercase + digits
    newname = "".join(choice(characters) for x in range(randint(8, 16)))
    newname += '.' + file_ext.lower()
    return newname


# resize image according to parameters in settings, used to create, for example, main image
# TODO: If we are going to attach images to reviews later
# import this this function from imagine app
def resize_image(file, options):
    # get extension
    m = re.search(".*\.(\w+)$", file.name)
    file_ext = m.group(1)
    file_ext = file_ext.lower()
    # generate filename
    filename = filename_gen(file_ext)

    # open source file
    src_image = default_storage.open(file.path)

    thumbnailer = get_thumbnailer(src_image, relative_name=filename)
    img = thumbnailer.generate_thumbnail(options)

    return (filename, img)
