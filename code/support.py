from os import walk
from PIL import Image
from settings import *
import re
import socket


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def get_images_from_dir(dir_name):
    surface_list = {}
    for _, __, img_files in walk(dir_name):
        for img in img_files:
            full_path = dir_name + '/' + img
            image_surf = Image.open(full_path)
            image_surf = image_surf.resize(PREFERRED_SIZE)
            image_surf.save(full_path)
            surface_list.update({full_path: image_surf})
    return surface_list


def is_pin_valid(new_val):
    if not new_val:
        return True
    result = re.match("[0-9a-zA-Z_\b]+$", new_val) is not None
    if not result or len(new_val) > 8:
        return False
    return True


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except TimeoutError:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def is_description_valid(new_val):
    if not new_val:
        return True
    result = re.match("[0-9a-zA-Zа-яА-Я_\-() ]+$", new_val) is not None
    if not result or len(new_val) > 25:
        return False
    return True


def is_prompt_valid(new_val):
    if not new_val:
        return True
    result = re.match("[0-9a-zA-Zа-яА-Я()\-=<>,/?.\"{}+!@$;:&*_`% ]+$", new_val) is not None
    if not result or len(new_val) > 50:
        return False
    return True


def is_valid(new_val):
    if not new_val:
        return True
    result = re.match("[0-9a-zA-Z_\-*() ]+$", new_val) is not None
    if not result or len(new_val) > 15:
        return False
    return True
