"""Generate a carrier image and a lossless steganographic video."""

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from stego_demo import hide

ROOT = Path(__file__).resolve().parent.parent
ROOT.joinpath("frames").mkdir(exist_ok=True)

width, height = 640, 360
for frame in range(24):
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                (x + frame * 4) % 256,
                (y * 2 + frame * 3) % 256,
                ((x + y) // 2 + frame * 5) % 256,
            )
    draw = ImageDraw.Draw(image)
    draw.text((28, 28), "DEMO DE ESTEGANOGRAFIA", fill=(255, 255, 255))
    draw.text((28, 55), f"frame {frame + 1:02d}/24", fill=(255, 230, 120))
    image.save(ROOT / "frames" / f"frame_{frame:03d}.png")

hide(
    ROOT / "frames" / "frame_000.png",
    ROOT / "demo_imagen.png",
    "Mensaje secreto de ejemplo: reunión a las 10:30.",
    "Clave-Demo-2026",
)

for frame_path in sorted((ROOT / "frames").glob("frame_*.png")):
    hide(
        frame_path,
        frame_path,
        "Video de demostración: datos protegidos con AES-GCM.",
        "Clave-Video-2026",
    )

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-framerate",
        "12",
        "-i",
        str(ROOT / "frames" / "frame_%03d.png"),
        "-c:v",
        "ffv1",
        str(ROOT / "demo_video.mkv"),
    ],
    check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
)
