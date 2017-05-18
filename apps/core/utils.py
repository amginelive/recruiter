from __future__ import (
    absolute_import,
    unicode_literals,
)

import os
import uuid


def get_upload_path(instance, filename):
    """
    This function gets the upload path of the image.
    Returns the image path.
    """
    file_name, file_extension = os.path.splitext(filename)
    model = instance._meta.model_name.lower()
    new_file = '{}{}'.format(uuid.uuid4().hex, file_extension)

    return os.path.join(model, new_file)
