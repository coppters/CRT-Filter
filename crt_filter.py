import os
import argparse
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import random

def apply_crt_filter(input_path, output_path, scanline_opacity=64, line_width=4):
    # Open the image
    img = Image.open(input_path).convert('RGB')
    width, height = img.size

    # Resize for pixelation
    pixelated = img.resize((width // 2, height // 2), Image.NEAREST).resize(img.size, Image.NEAREST)

    # Create horizontal scanlines with blending (semi-transparent black lines)
    scanline_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(scanline_img)
    for y in range(0, height, line_width * 2):
        draw.rectangle([0, y, width, y + line_width], fill=(0, 0, 0, scanline_opacity))  # Semi-transparent black lines

    # Overlay scanlines on pixelated image
    pixelated = pixelated.convert("RGBA")
    combined = Image.alpha_composite(pixelated, scanline_img)

    # Add corner curvature (vignette effect)
    vignette = Image.new('L', (width, height), 255)  # Start with a white mask
    draw = ImageDraw.Draw(vignette)
    for y in range(height):
        for x in range(width):
            # Calculate distance from the center
            distance = ((x - width / 2) ** 2 + (y - height / 2) ** 2) ** 0.5
            max_distance = (width / 2) ** 2 + (height / 2) ** 2
            brightness = int(255 * (1 - (distance / max_distance) ** 0.6))  # Adjust curvature intensity
            vignette.putpixel((x, y), max(0, brightness))
    vignette_blur = vignette.filter(ImageFilter.GaussianBlur(radius=30))  # Smooth the curvature
    combined = Image.composite(combined, Image.new('RGB', (width, height), (0, 0, 0)), vignette_blur)

    # Enhance color vibrancy
    enhancer = ImageEnhance.Color(combined.convert("RGB"))
    combined = enhancer.enhance(1.5)  # Increase color saturation

    # Add subtle noise
    combined = combined.convert("RGB")  # Ensure compatibility for noise addition
    noise_intensity = 0.02  # 2% noise
    noise_img = combined.load()
    for y in range(height):
        for x in range(width):
            if random.random() < noise_intensity:
                r, g, b = noise_img[x, y]
                noise_img[x, y] = (
                    min(255, max(0, r + random.randint(-20, 20))),
                    min(255, max(0, g + random.randint(-20, 20))),
                    min(255, max(0, b + random.randint(-20, 20))),
                )

    # Save the result
    combined.save(output_path)
    print(f"Processed: {output_path}")

def batch_process(input_folder, output_folder, scanline_opacity, line_width):
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            apply_crt_filter(input_path, output_path, scanline_opacity, line_width)

def main():
    parser = argparse.ArgumentParser(description="Apply CRT-like filters to images.")
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input folder containing images."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to the output folder where processed images will be saved."
    )
    parser.add_argument(
        "-s", "--scanline_opacity", type=int, default=64, help="Opacity of the scanlines (0-255). Default: 64"
    )
    parser.add_argument(
        "-l", "--line_width", type=int, default=4, help="Width of the scanlines. Default: 4"
    )
    args = parser.parse_args()

    # Run batch processing
    batch_process(args.input, args.output, args.scanline_opacity, args.line_width)

if __name__ == "__main__":
    main()
