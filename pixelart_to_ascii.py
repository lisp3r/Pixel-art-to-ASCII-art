import os.path
import argparse
from json import dumps
from PIL import Image


def get_colors(img: Image) -> dict:
    '''Getting RGB colors from strange PIL palette.'''

    width, height = img.size
    dict_num = dict(img.getcolors(width*height))
    dict_rgb = dict(img.convert('RGB').getcolors(width*height))
    return {str(dict_num[key]): f'rgb{dict_rgb[key]}' for key in dict_rgb}

def img_to_list(img: Image) -> list:
    '''Convert PIL.Image to pixel map'''

    pixels = list(img.getdata())
    width, height = img.size
    return [pixels[i * width:(i + 1) * width] for i in range(height)]

def get_pixel_size(img: list) -> int:
    '''Calculate size of one pixel on source image.'''
    equals = 0
    row = img[0]

    for i in range(len(img)):
        if img[1] == row:
            equals = equals+1
            row = img[i+1]
    return equals # num of true pixels from one source's pixel

def resize_img(img: list, pix_size: int) -> list:
    '''Having a source's pixel size, removeng extra rows and cols.'''

    y_resized = [elem for num, elem in enumerate(img) if elem not in img[:num]]
    new_img = []
    for row in y_resized:
        new_img.append(row[::pix_size])
    return new_img

def get_ascii(img: list) -> str:
    new_img = ""
    for x in img:
        new_img += ''.join([str(y) for y in x])
        new_img += '\n'
    return new_img

def print_ascii(img: list):
    print(get_ascii(img))

def _write_down(data: str, file: str):
    with open(file, 'w') as f:
        f.write(data)

def to_plain_text(images: list, colors: dict, file: str):
    str_colors = '\n'.join([f'{x}: {colors[x]}' for x in colors])
    if len(images) == 1:
        _write_down(f'{images[0]}\n\n{str_colors}', f'{file}.txt')
    else:
        n = 1
        for img in images:
            _write_down(f'{img}\n\n{str_colors}', f'{file}_{n}.txt')
            n = n+1

def to_json(images: list, colors: dict, file: str):
    json_dict = {
        "images": images,
        "colors": colors
    }
    _write_down(dumps(json_dict), f'{file}.json')

def process_img(pil_image: Image):
    im_pixels = img_to_list(pil_image)
    im_resized = resize_img(im_pixels, get_pixel_size(im_pixels))
    return get_ascii(im_resized)

def process_gif(pil_image: Image):
    frames = []
    for frame in range(0, pil_image.n_frames):
        pil_image.seek(frame)
        frames.append(process_img(pil_image))
    return frames


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert pixelart image to ascii art')

    parser.add_argument('image', metavar='img', help='Image (gif, png)')
    parser.add_argument('--json', action="store_true", help='Output result json file')

    ARGS = parser.parse_args()

    IMG_FILE_NAME = os.path.split(ARGS.image)[-1]
    
    IMAGE = Image.open(ARGS.image)
    COLORS = get_colors(IMAGE)

    ascii_img_list = process_gif(IMAGE) if IMAGE.is_animated else [process_img(IMAGE)]

    if ARGS.json:
        to_json(ascii_img_list, COLORS, IMG_FILE_NAME)
    else:
        to_plain_text(ascii_img_list, COLORS, IMG_FILE_NAME)
