import sys, os
from PIL import Image, ImageDraw, ImageFont

# Todo: UI for this

def load_args():
    img_logo = sys.argv[3]
    position = sys.argv[4]
    # Ratio format: "5:2" (image:watermark ratio)
    ratio = sys.argv[5] if len(sys.argv) > 5 else "5:2"
    
    if "." in sys.argv[1]:
        img_input = sys.argv[1]
        img_output = sys.argv[2]
        watermark_logo_image(img_input, img_output, img_logo, position, ratio)
    else:
        folder_input = sys.argv[1]
        folder_output = sys.argv[2]
        watermark_logo_images(folder_input, folder_output, img_logo, position, ratio)
        

def usage():
    print(" ----------------------------Logo---------------------------------")
    print("| Usage: water.py input.jpg output.jpg logo.png position [ratio]    |")
    print("| Usage: water.py /folder_input /folder_output logo.png position [ratio] |")
    print(" ----------------------------------------------------------------")
    print("| position = topleft/topright/center/bottomleft/bottomright      |")
    print("| ratio = image:watermark (default 5:2)                          |")
    print("| Examples:                                                       |")
    print("| water.py input.jpg output.jpg logo.png bottomright 5:2            |")
    print("| water.py input.jpg output.jpg logo.png bottomright 4:1 (smaller)  |")
    print("| water.py input.jpg output.jpg logo.png bottomright 3:1 (larger)   |")
    print("| water.py ./images ./output logo.png bottomright 6:2               |")
    print(" -----------------------------------------------------------------")


def parse_ratio(ratio_string):
    """
    Parse ratio string like "5:2" and return the decimal ratio
    
    Args:
        ratio_string: String like "5:2", "4:1", "3:2"
    
    Returns:
        float: The watermark ratio (e.g., 0.4 for 5:2)
    """
    try:
        parts = ratio_string.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid ratio format")
        
        image_ratio = float(parts[0])
        watermark_ratio = float(parts[1])
        
        if image_ratio <= 0 or watermark_ratio <= 0:
            raise ValueError("Ratio parts must be positive")
        
        # Calculate the watermark size as a fraction of image size
        decimal_ratio = watermark_ratio / image_ratio
        
        print(f"Using ratio {ratio_string} → watermark will be {decimal_ratio:.2%} of image width")
        return decimal_ratio
        
    except (ValueError, IndexError):
        print(f"Invalid ratio '{ratio_string}'. Using default 5:2")
        return 0.4  # Default 5:2 ratio


def resize_logo_by_ratio(logo, image, ratio_string="5:2"):
    """
    Resize logo based on image-to-watermark ratio
    
    Args:
        logo: PIL Image object of the logo
        image: PIL Image object of the main image
        ratio_string: Ratio like "5:2" (image:watermark)
    """
    # Parse the ratio
    watermark_ratio = parse_ratio(ratio_string)
    
    # Calculate target width based on image width and ratio
    target_width = int(image.size[0] * watermark_ratio)
    
    # Calculate proportional height to maintain logo aspect ratio
    logo_aspect_ratio = logo.size[1] / logo.size[0]
    target_height = int(target_width * logo_aspect_ratio)
    
    # Resize logo
    resized_logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    print(f"Image size: {image.size}")
    print(f"Logo resized from {logo.size} to {resized_logo.size}")
    print(f"Watermark is {watermark_ratio:.1%} of image width")
    
    return resized_logo


def get_position(logo, image, pos):
    """Get watermark position coordinates with margin"""
    margin = 20  # Add some margin from edges
    
    if pos == "topleft": 
        return (margin, margin)
    if pos == "bottomleft": 
        return (margin, image.size[1] - logo.size[1] - margin)
    if pos == "topright": 
        return (image.size[0] - logo.size[0] - margin, margin)
    if pos == "bottomright": 
        return (image.size[0] - logo.size[0] - margin, image.size[1] - logo.size[1] - margin)
    if pos == "center": 
        return (int((image.size[0] - logo.size[0]) / 2), int((image.size[1] - logo.size[1]) / 2))
    
    # Default to bottomright
    return (image.size[0] - logo.size[0] - margin, image.size[1] - logo.size[1] - margin)


def watermark_logo_image(i, o, l, p, ratio="5:2"):
    """Add watermark to a single image using ratio-based sizing"""
    try:
        logo = Image.open(l)
        image = Image.open(i)
        
        # Resize logo based on image size and ratio
        logo = resize_logo_by_ratio(logo, image, ratio)
        
        # Convert to RGBA for better transparency support
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Get position
        position = get_position(logo, image, p)
        
        # Paste logo with transparency
        image.paste(logo, position, logo)
        
        # Convert back to RGB for JPEG saving
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        image.save(o)
        return True
        
    except Exception as e:
        print(f"Error processing {i}: {e}")
        return False


def watermark_logo_images(i, o, l, p, ratio="5:2"):
    """Add watermark to all images in a folder"""
    # Create output directory if it doesn't exist
    if not os.path.exists(o):
        os.makedirs(o)
        print(f"Created output directory: {o}")
    
    # Case-insensitive extension check
    extensions = ['png', 'bmp', 'jpg', 'gif', 'jpeg', 'PNG', 'BMP', 'JPG', 'GIF', 'JPEG']
    
    try:
        files = os.listdir(i)
    except OSError as e:
        print(f"Error accessing input directory {i}: {e}")
        return
    
    # Count only image files for accurate progress
    image_files = [file for file in files if any(file.endswith(ext) for ext in extensions)]
    total_images = len(image_files)
    
    if total_images == 0:
        print("No image files found in the input directory.")
        return
    
    print(f"Found {total_images} image files to process with ratio {ratio}...")
    print("-" * 60)
    
    processed = 0
    successful = 0
    
    for file in image_files:
        input_path = os.path.join(i, file)
        output_path = os.path.join(o, file)
        
        print(f"\nProcessing {file} ({processed + 1} of {total_images})...")
        
        if watermark_logo_image(input_path, output_path, l, p, ratio):
            successful += 1
            print(f"✓ Successfully processed: {file}")
        else:
            print(f"✗ Failed to process: {file}")
        
        processed += 1
    
    print(f"\n🎉 Batch complete: {successful}/{total_images} images processed successfully.")


def validate_inputs():
    """Validate command line arguments"""
    if len(sys.argv) < 5:
        return False
    
    logo_path = sys.argv[3]
    position = sys.argv[4]
    
    # Check if logo file exists
    if not os.path.exists(logo_path):
        print(f"Error: Logo file '{logo_path}' not found.")
        return False
    
    # Check if position is valid
    valid_positions = ['topleft', 'topright', 'center', 'bottomleft', 'bottomright']
    if position not in valid_positions:
        print(f"Error: Invalid position '{position}'. Use one of: {', '.join(valid_positions)}")
        return False
    
    # Check input path
    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"Error: Input path '{input_path}' not found.")
        return False
    
    # Validate ratio if provided
    if len(sys.argv) > 5:
        ratio = sys.argv[5]
        if ':' not in ratio:
            print("Error: Ratio must be in format 'image:watermark' (e.g., '5:2', '4:1')")
            return False
    
    return True


if __name__ == "__main__":
    if not validate_inputs():
        usage()
    else:
        try:
            load_args()
            print("\n🎉 Watermark process completed!")
        except Exception as e:
            print(f'Error: {e}')
            usage()         