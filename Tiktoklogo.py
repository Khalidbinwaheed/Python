import svgwrite
import numpy as np
from PIL import Image  # Pillow
import cairosvg
import os
import logging
import datetime

# --- Configuration ---
OUTPUT_DIR = "tiktok_logo_output"
BASE_FILENAME = "tiktok_style_logo"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SVG_FILENAME = f"{BASE_FILENAME}_{TIMESTAMP}.svg"
PNG_FILENAME = f"{BASE_FILENAME}_{TIMESTAMP}.png"
PNG_RESOLUTION = 512  # Output width/height for PNG in pixels

# SVG Canvas Size
WIDTH = 200
HEIGHT = 200

# Colors (using numpy for demonstration, though simple tuples work too)
# TikTok uses specific shades, these are approximations
COLOR_BLACK = np.array([0, 0, 0])
COLOR_CYAN = np.array([40, 240, 240]) # Approx Aqua/Cyan
COLOR_MAGENTA = np.array([255, 0, 80]) # Approx Pink/Magenta

# Glitch effect offset
OFFSET_X = 5

# Shape parameters
NOTE_HEAD_CX = 80
NOTE_HEAD_CY = 130
NOTE_HEAD_R = 30
STEM_X = NOTE_HEAD_CX + NOTE_HEAD_R # Start stem at edge of circle
STEM_Y_BOTTOM = NOTE_HEAD_CY
STEM_Y_TOP = 50
STEM_WIDTH = 20
FLAG_CONTROL_X = 150
FLAG_CONTROL_Y = 40
FLAG_END_X = 160
FLAG_END_Y = 90

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Function ---
def np_color_to_rgb_string(np_color):
    """Converts a numpy color array to an 'rgb(r,g,b)' string."""
    return f"rgb({int(np_color[0])},{int(np_color[1])},{int(np_color[2])})"

# --- Main Logic ---
def create_tiktok_style_logo(output_svg_path, output_png_path=None, png_res=512):
    """
    Generates the TikTok-style logo as an SVG and optionally converts to PNG.
    """
    logging.info(f"Starting logo generation. Output SVG: {output_svg_path}")

    # Create SVG Drawing
    dwg = svgwrite.Drawing(output_svg_path, size=(f"{WIDTH}px", f"{HEIGHT}px"), profile='tiny', viewBox=f"0 0 {WIDTH} {HEIGHT}")

    # Define the core shape path (stem + flag)
    # M = MoveTo, L = LineTo, Q = Quadratic Bezier Curve
    # Path starts at bottom of stem, goes up, then curves for the flag
    path_d = f"M {STEM_X} {STEM_Y_BOTTOM} L {STEM_X} {STEM_Y_TOP} Q {FLAG_CONTROL_X} {FLAG_CONTROL_Y} {FLAG_END_X} {FLAG_END_Y}"

    # --- Draw Glitch Layers (behind) ---

    # Cyan Layer (Offset Right)
    cyan_group = dwg.g(transform=f"translate({OFFSET_X}, 0)")
    cyan_color_str = np_color_to_rgb_string(COLOR_CYAN)
    # Cyan Path (Stem + Flag)
    cyan_group.add(dwg.path(d=path_d,
                            stroke=cyan_color_str,
                            stroke_width=STEM_WIDTH,
                            stroke_linecap='round', # Smoother ends
                            fill='none'))
    # Cyan Circle (Note Head)
    cyan_group.add(dwg.circle(center=(NOTE_HEAD_CX, NOTE_HEAD_CY),
                              r=NOTE_HEAD_R,
                              fill=cyan_color_str))
    dwg.add(cyan_group)
    logging.info("Added Cyan layer.")

    # Magenta Layer (Offset Left)
    magenta_group = dwg.g(transform=f"translate({-OFFSET_X}, 0)")
    magenta_color_str = np_color_to_rgb_string(COLOR_MAGENTA)
    # Magenta Path (Stem + Flag)
    magenta_group.add(dwg.path(d=path_d,
                               stroke=magenta_color_str,
                               stroke_width=STEM_WIDTH,
                               stroke_linecap='round',
                               fill='none'))
    # Magenta Circle (Note Head)
    magenta_group.add(dwg.circle(center=(NOTE_HEAD_CX, NOTE_HEAD_CY),
                                 r=NOTE_HEAD_R,
                                 fill=magenta_color_str))
    dwg.add(magenta_group)
    logging.info("Added Magenta layer.")

    # --- Draw Main Black Layer (on top) ---
    black_color_str = np_color_to_rgb_string(COLOR_BLACK)
    # Black Path (Stem + Flag)
    dwg.add(dwg.path(d=path_d,
                     stroke=black_color_str,
                     stroke_width=STEM_WIDTH,
                     stroke_linecap='round',
                     fill='none'))
    # Black Circle (Note Head)
    dwg.add(dwg.circle(center=(NOTE_HEAD_CX, NOTE_HEAD_CY),
                       r=NOTE_HEAD_R,
                       fill=black_color_str))
    logging.info("Added Black layer.")

    # Save SVG file
    try:
        dwg.save(pretty=True) # pretty=True makes the SVG file readable
        logging.info(f"SVG logo saved successfully to {output_svg_path}")
    except Exception as e:
        logging.error(f"Error saving SVG file: {e}")
        return False

    # --- Optional: Convert SVG to PNG using cairosvg and Pillow ---
    if output_png_path:
        logging.info(f"Attempting to convert SVG to PNG: {output_png_path}")
        try:
            cairosvg.svg2png(url=output_svg_path, write_to=output_png_path, output_width=png_res, output_height=png_res)
            # Optionally open with Pillow to verify or further process
            # img = Image.open(output_png_path)
            # img.show() # Example: display the image
            logging.info(f"PNG logo saved successfully to {output_png_path} with resolution {png_res}x{png_res}")
        except ImportError:
             logging.warning("`cairosvg` library not found or failed. Skipping PNG conversion. Install with `pip install cairosvg`.")
        except Exception as e:
            logging.error(f"Error converting SVG to PNG: {e}")
            # Attempt Pillow conversion as a fallback (might not render well)
            # try:
            #     from svglib.svglib import svg2rlg
            #     from reportlab.graphics import renderPM
            #     drawing = svg2rlg(output_svg_path)
            #     renderPM.drawToFile(drawing, output_png_path, fmt="PNG")
            #     logging.info("PNG conversion fallback using svglib/reportlab succeeded.")
            # except Exception as e2:
            #      logging.error(f"Pillow/svglib fallback for PNG conversion also failed: {e2}")


    return True

# --- Execution ---
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logging.info(f"Created output directory: {OUTPUT_DIR}")

    svg_file = os.path.join(OUTPUT_DIR, SVG_FILENAME)
    png_file = os.path.join(OUTPUT_DIR, PNG_FILENAME)

    # Generate the logo (SVG and PNG)
    success = create_tiktok_style_logo(svg_file, png_file, PNG_RESOLUTION)

    if success:
        logging.info("Logo generation process completed.")
    else:
        logging.error("Logo generation process failed.")