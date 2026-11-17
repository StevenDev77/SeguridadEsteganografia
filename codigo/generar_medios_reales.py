"""Create realistic-looking stego examples from public-domain NASA photographs."""

from pathlib import Path
import shutil
import subprocess
import urllib.request
import math

from PIL import Image, ImageDraw, ImageFont

from stego_demo import hide

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "frames_astronauta"
FRAMES.mkdir(exist_ok=True)

ASTRONAUT_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/5/53/"
    "Spaceship_Earth_%28art002e008487%29.jpg"
)
EARTH_URL = (
    "https://images-assets.nasa.gov/image/iss028e020072/"
    "iss028e020072~orig.jpg"
)


def download(url: str, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "stego-demo/1.0"})
    with urllib.request.urlopen(request) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


def make_image(source: Path, destination: Path, message: str, password: str) -> None:
    image = Image.open(source).convert("RGB")
    image.thumbnail((1600, 1200))
    image.save(destination.with_name(destination.stem + "_original.png"))
    hide(destination.with_name(destination.stem + "_original.png"), destination, message, password)


def make_video(source: Path) -> None:
    image = Image.open(source).convert("RGB")
    font = ImageFont.load_default()
    for index in range(72):
        # Simulate a slow handheld/inspection camera move over the photograph.
        zoom = 1.0 + 0.12 * (index / 71)
        scaled = image.resize((round(960 * zoom), round(720 * zoom)))
        travel_x = round((scaled.width - 960) * (0.5 + 0.5 * math.sin(index / 18)))
        travel_y = round((scaled.height - 720) * (0.5 + 0.5 * math.cos(index / 22)))
        frame = scaled.crop((travel_x, travel_y, travel_x + 960, travel_y + 720))
        draw = ImageDraw.Draw(frame)
        draw.rectangle((22, 22, 938, 116), fill=(0, 12, 20), outline=(46, 220, 180), width=2)
        draw.text((40, 38), "ORION // DEEP SPACE TELEMETRY", fill=(120, 255, 210), font=font)
        draw.text(
            (40, 62),
            f"UTC 2026-11-17 05:{index // 12:02d}:{(index % 12) * 5:02d}   "
            f"CAM-01  SIGNAL {98 + index % 3}%",
            fill=(210, 240, 235),
            font=font,
        )
        draw.text(
            (40, 86),
            "OPTICAL LINK: NOMINAL   FRAME: "
            f"{index + 1:04d}   LOSSLESS ARCHIVE",
            fill=(120, 255, 210),
            font=font,
        )
        path = FRAMES / f"frame_{index:03d}.png"
        frame.save(path)
        hide(path, path,         "Hackeado por estudiantes de software", "Orion-2026")
    subprocess.run(
        [
            "ffmpeg", "-y", "-framerate", "12", "-i",
            str(FRAMES / "frame_%03d.png"), "-c:v", "ffv1",
            str(ROOT / "astronauta_consola.mkv"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def main() -> None:
    astronauta = ROOT / "astronauta_fuente.jpg"
    tierra = ROOT / "tierra_fuente.jpg"
    download(ASTRONAUT_URL, astronauta)
    download(EARTH_URL, tierra)
    make_image(
        tierra,
        ROOT / "tierra_esteganografia.png",
        "Mensaje oculto en una fotografía real: la Tierra sigue siendo nuestro hogar.",
        "Tierra-2026",
    )
    make_image(
        astronauta,
        ROOT / "astronauta_esteganografia.png",
        "Hackeado por estudiantes de software",
        "Astronauta-2026",
    )
    make_video(astronauta)


if __name__ == "__main__":
    main()
