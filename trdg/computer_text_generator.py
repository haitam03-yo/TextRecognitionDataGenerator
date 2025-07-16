import random as rnd
from typing import Tuple
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

from trdg.utils import get_text_width, get_text_height

import textwrap
import random as rnd

# Thai Unicode reference: https://jrgraphix.net/r/Unicode/0E00-0E7F
TH_TONE_MARKS = [
    "0xe47",
    "0xe48",
    "0xe49",
    "0xe4a",
    "0xe4b",
    "0xe4c",
    "0xe4d",
    "0xe4e",
]
TH_UNDER_VOWELS = ["0xe38", "0xe39", "\0xe3A"]
TH_UPPER_VOWELS = ["0xe31", "0xe34", "0xe35", "0xe36", "0xe37"]


def generate(
    text: str,
    font: str,
    text_color: str,
    font_size: int,
    orientation: int,
    space_width: int,
    character_spacing: int,
    fit: bool,
    word_split: bool,
    stroke_width: int = 0,
    stroke_fill: str = "#282828",
) -> Tuple:
    if orientation == 0:
        return _generate_horizontal_text(
            text,
            font,
            text_color,
            font_size,
            space_width,
            character_spacing,
            fit,
            word_split,
            stroke_width,
            stroke_fill,
        )
    elif orientation == 1:
        return _generate_vertical_text(
            text,
            font,
            text_color,
            font_size,
            space_width,
            character_spacing,
            fit,
            stroke_width,
            stroke_fill,
        )
    elif orientation == 2:
        return _generate_paragraph_text(
            text,
            font,
            text_color,
            font_size,
            space_width,
            character_spacing,
            fit,
            stroke_width,
            stroke_fill,
        )
    else:
        raise ValueError("Unknown orientation " + str(orientation))


def _compute_character_width(image_font: ImageFont, character: str) -> int:
    if len(character) == 1 and (
        "{0:#x}".format(ord(character))
        in TH_TONE_MARKS + TH_UNDER_VOWELS + TH_UNDER_VOWELS + TH_UPPER_VOWELS
    ):
        return 0
    # Casting as int to preserve the old behavior
    return round(image_font.getlength(character))


def _generate_horizontal_text(
    text: str,
    font: str,
    text_color: str,
    font_size: int,
    space_width: int,
    character_spacing: int,
    fit: bool,
    word_split: bool,
    stroke_width: int = 0,
    stroke_fill: str = "#282828",
) -> Tuple:
    image_font = ImageFont.truetype(font=font, size=font_size)

    space_width = int(get_text_width(image_font, " ") * space_width)

    if word_split:
        splitted_text = []
        for w in text.split(" "):
            splitted_text.append(w)
            splitted_text.append(" ")
        splitted_text.pop()
    else:
        splitted_text = text

    piece_widths = [
        _compute_character_width(image_font, p) if p != " " else space_width
        for p in splitted_text
    ]
    text_width = sum(piece_widths)
    if not word_split:
        text_width += character_spacing * (len(text) - 1)

    text_height = max([get_text_height(image_font, p) for p in splitted_text])

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGB", (text_width, text_height), (0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_mask, mode="RGB")
    txt_mask_draw.fontmode = "1"

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(min(c1[0], c2[0]), max(c1[0], c2[0])),
        rnd.randint(min(c1[1], c2[1]), max(c1[1], c2[1])),
        rnd.randint(min(c1[2], c2[2]), max(c1[2], c2[2])),
    )

    stroke_colors = [ImageColor.getrgb(c) for c in stroke_fill.split(",")]
    stroke_c1, stroke_c2 = stroke_colors[0], stroke_colors[-1]

    stroke_fill = (
        rnd.randint(min(stroke_c1[0], stroke_c2[0]), max(stroke_c1[0], stroke_c2[0])),
        rnd.randint(min(stroke_c1[1], stroke_c2[1]), max(stroke_c1[1], stroke_c2[1])),
        rnd.randint(min(stroke_c1[2], stroke_c2[2]), max(stroke_c1[2], stroke_c2[2])),
    )

    for i, p in enumerate(splitted_text):
        txt_img_draw.text(
            (sum(piece_widths[0:i]) + i * character_spacing * int(not word_split), 0),
            p,
            fill=fill,
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        txt_mask_draw.text(
            (sum(piece_widths[0:i]) + i * character_spacing * int(not word_split), 0),
            p,
            fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255),
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask


def _generate_vertical_text(
    text: str,
    font: str,
    text_color: str,
    font_size: int,
    space_width: int,
    character_spacing: int,
    fit: bool,
    stroke_width: int = 0,
    stroke_fill: str = "#282828",
) -> Tuple:
    image_font = ImageFont.truetype(font=font, size=font_size)

    space_height = int(get_text_height(image_font, " ") * space_width)

    char_heights = [
        get_text_height(image_font, c) if c != " " else space_height for c in text
    ]
    text_width = max([get_text_width(image_font, c) for c in text])
    text_height = sum(char_heights) + character_spacing * len(text)

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_mask)
    txt_mask_draw.fontmode = "1"

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(c1[0], c2[0]),
        rnd.randint(c1[1], c2[1]),
        rnd.randint(c1[2], c2[2]),
    )

    stroke_colors = [ImageColor.getrgb(c) for c in stroke_fill.split(",")]
    stroke_c1, stroke_c2 = stroke_colors[0], stroke_colors[-1]

    stroke_fill = (
        rnd.randint(stroke_c1[0], stroke_c2[0]),
        rnd.randint(stroke_c1[1], stroke_c2[1]),
        rnd.randint(stroke_c1[2], stroke_c2[2]),
    )

    for i, c in enumerate(text):
        txt_img_draw.text(
            (0, sum(char_heights[0:i]) + i * character_spacing),
            c,
            fill=fill,
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        txt_mask_draw.text(
            (0, sum(char_heights[0:i]) + i * character_spacing),
            c,
            fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255),
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask


def get_text_width(font, text):
    return font.getbbox(text)[2]

def get_text_height(font, text):
    if not text:
        return font.getbbox("ا")[3]
    return font.getbbox(text)[3]

def wrap_text_by_pixels(text, font, max_width, max_lines):
    lines = []
    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        words = paragraph.split()
            
        current_line = ''
        
        for word in words:
            if len(lines) >= max_lines:
                break

            test_line = current_line + (" " if current_line else "") + word
            w = get_text_width(font, test_line)
            if w <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if len(lines) < max_lines:
            lines.append(current_line)


    return lines[:max_lines]


def _generate_paragraph_text(
    text: str,
    font: str,
    text_color: str,
    font_size: int,
    space_width: int,
    character_spacing: int,
    fit: bool,
    stroke_width: int = 0,
    stroke_fill: str = "#282828",
    max_text_height: int = 1350,
    max_lines: int = 11
) -> Tuple:
    print(text)
    contains_title = False
    flag = False
    # Load font
    if isinstance(font_size, list):
        font_size = rnd.randint(font_size[0], font_size[1])

        
    image_font = ImageFont.truetype(font=font, size=font_size)
    
    title = ''
    if isinstance(text, dict):
        title = text.get("title","أطلسيا")
        text = text.get("content","")
        print('dict')

    # Dynamically estimate max width from text length
    estimated_width = min(len(text) * font_size // 1.5, 1000)  # reasonable upper bound
    max_width = max(int(estimated_width), 200)
    
    min_default_width = rnd.choice([800, 1000, 1500, 1600])
    estimated_width = min(len(text) * font_size // 1.5, min_default_width)
    max_width = max(int(estimated_width), 800)

    # Wrap Arabic text to fit max width
    
    
    lines = wrap_text_by_pixels(text, image_font, max_width, max_lines)
    if title:
        rnd_num = rnd.random()
        if rnd_num<0.5:
            lines.insert(0, '')
        else:
            lines.insert(0, '─')
        lines.insert(0, title)
        contains_title = True
    
    # Recalculate text height
    line_heights = [get_text_height(image_font, line) for line in lines]
    character_spacing = rnd.randint(1,4)  # or your config value
    text_height = sum(line_heights) + (len(lines) - 1) * character_spacing
    text_width = max([get_text_width(image_font, line) for line in lines])
    # Trim lines if total height is too big
    while text_height > max_text_height and len(lines) > 1:
        lines = lines[:-1]  # remove last line
        line_heights = [get_text_height(image_font, line) for line in lines]
        text_height = sum(line_heights) + (len(lines) - 1) * character_spacing

        
        text_width = max([get_text_width(image_font, line) for line in lines])

    # Create images
    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGB", (text_width, text_height), (0, 0, 0))

    draw = ImageDraw.Draw(txt_img)
    draw_mask = ImageDraw.Draw(txt_mask)
    draw_mask.fontmode = "1"

    # Random text color within range
    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]
    fill = (
        rnd.randint(c1[0], c2[0]),
        rnd.randint(c1[1], c2[1]),
        rnd.randint(c1[2], c2[2]),
    )

    # Random stroke color within range
    stroke_colors = [ImageColor.getrgb(c) for c in stroke_fill.split(",")]
    stroke_c1, stroke_c2 = stroke_colors[0], stroke_colors[-1]
    stroke_fill = (
        rnd.randint(stroke_c1[0], stroke_c2[0]),
        rnd.randint(stroke_c1[1], stroke_c2[1]),
        rnd.randint(stroke_c1[2], stroke_c2[2]),
    )

    # Draw text and mask
    current_y = 0
    original_image_font = image_font
    for i, line in enumerate(lines): 
        if line=='':
            #last_added_y = get_text_height(image_font, 'اب') + character_spacing
            last_added_y = line_heights[i] + character_spacing
            current_y += last_added_y//2
            
            continue
        
        if line == "─":
            image_font = ImageFont.truetype(font="/usr/share/fonts/truetype/noto/NotoSansMono-Light.ttf", size=font_size)
            flag = True
            
        line_w = get_text_width(image_font, line)
        x = text_width - line_w 
        if contains_title and i == 0:
            rnd_num = rnd.random()
            if rnd_num<0.5:
                x  = max(0, (text_width - line_w) // 2)  # center
        
        if line == "─":
            while line_w<(3*text_width/4):
                line += line
                line_w = get_text_width(image_font, line)
            
            x  = max(0, (text_width - line_w) // 2)  # center
            
            
            

        draw.text( 
            (x, current_y), 
            line, 
            fill=fill, 
            font=image_font, 
            stroke_width=stroke_width, 
            stroke_fill=stroke_fill, 
        ) 
        draw_mask.text( 
            (x, current_y), 
            line, 
            fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255), 
            font=image_font, 
            stroke_width=stroke_width, 
            stroke_fill=stroke_fill, 
        ) 
        last_added_y = line_heights[i] + character_spacing
        current_y += last_added_y
        if flag:
            image_font = original_image_font


    label = " ".join([line.replace("─", "") for line in lines if line.strip()][::-1])
    print(contains_title)
    meta_data = {
        "text": label,
        "font": font.split("/")[-1].split(".")[0],
        "contains_title": contains_title,
    }
    if fit:
        bbox = txt_img.getbbox()
        if bbox:  # In case bbox is None (completely transparent)
            txt_img = txt_img.crop(bbox)
            txt_mask = txt_mask.crop(bbox)
            
    return txt_img, txt_mask, meta_data

if __name__ == "__main__":
    example_text = {
        "title": "عنوان المثال",
        "content": "هذا نص طويل لاختبار توليد الصورة بالنص العربي."
    }

    img, mask, meta = _generate_paragraph_text(
        text=example_text,
        font="/usr/share/fonts/custom-arabic/NotoKufiArabic-Black.ttf",  # Update to your actual path
        text_color="#000000,#000000",
        font_size=32,
        space_width=10,
        character_spacing=5,
        fit=True,
    )

    img.save("test_img.png")
    print("Metadata:", meta)

    