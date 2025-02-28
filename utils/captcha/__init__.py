from PIL import Image, ImageDraw, ImageFont

def generate_captcha(text: str = None, width: int = 300, height: int = 100) -> Image:
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200))
    
    # Load a larger font (make sure 'arial.ttf' or another valid font is available)
    try:
        font = ImageFont.truetype("arial.ttf", 48)  # Adjust size as needed
    except IOError:
        font = ImageFont.load_default()  # Fallback in case the font isn't found
    
    # Get text size for positioning
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2 - text_bbox[0]  
    y = (height - text_height) // 2 - text_bbox[1]  
    
    draw.text((x, y), text, font=font, fill=(0, 0, 0))
    
    return image