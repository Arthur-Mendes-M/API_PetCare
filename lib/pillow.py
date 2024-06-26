import os
from PIL import Image
import tempfile

def validate_image(image_as_byte):
    valid_image_formats = ['jpg', 'jpeg', 'png']

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(image_as_byte)
        image_path = temp_file.name  

    image = Image.open(image_path)
    image_size = os.path.getsize(image_path)
    image_size_mb = image_size / (1024 * 1024)

    image_format = image.format.lower()

    return image_format in valid_image_formats and image_size_mb <= 3