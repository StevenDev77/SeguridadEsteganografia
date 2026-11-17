"""Educational PNG/video steganography demo.

The payload is encrypted with AES-256-GCM. The encrypted package is then
stored in the least-significant bits of RGB bytes. Use lossless carriers:
lossy JPEG/MP4 encoding can destroy the hidden bits.
"""

from __future__ import annotations

import argparse
import hashlib
import secrets
import struct
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image

MAGIC = b"STG1"
SALT_SIZE = 16
NONCE_SIZE = 12
HEADER_SIZE = 4 + SALT_SIZE + NONCE_SIZE + 4
PBKDF2_ROUNDS = 600_000


def _key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS, dklen=32
    )


def encrypt(message: str, password: str) -> bytes:
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    ciphertext = AESGCM(_key(password, salt)).encrypt(
        nonce, message.encode("utf-8"), None
    )
    return MAGIC + salt + nonce + struct.pack(">I", len(ciphertext)) + ciphertext


def decrypt(package: bytes, password: str) -> str:
    if len(package) < HEADER_SIZE or package[:4] != MAGIC:
        raise ValueError("No se encontró un paquete STG1 válido.")
    salt = package[4:20]
    nonce = package[20:32]
    length = struct.unpack(">I", package[32:36])[0]
    ciphertext = package[36 : 36 + length]
    if len(ciphertext) != length:
        raise ValueError("El paquete está incompleto o dañado.")
    try:
        plaintext = AESGCM(_key(password, salt)).decrypt(nonce, ciphertext, None)
    except InvalidTag as exc:
        raise ValueError("Contraseña incorrecta o datos alterados.") from exc
    return plaintext.decode("utf-8")


def _bits(data: bytes):
    for byte in data:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


def _read_bits(values: bytes, count: int) -> bytes:
    output = bytearray()
    for offset in range(0, count, 8):
        byte = 0
        for bit in values[offset : offset + 8]:
            byte = (byte << 1) | bit
        output.append(byte)
    return bytes(output)


def hide(input_path: Path, output_path: Path, message: str, password: str) -> None:
    image = Image.open(input_path).convert("RGB")
    pixels = bytearray(image.tobytes())
    package = encrypt(message, password)
    required = len(package) * 8
    if required > len(pixels):
        raise ValueError(
            f"Mensaje demasiado grande: requiere {required} bits y hay {len(pixels)}."
        )
    for index, bit in enumerate(_bits(package)):
        pixels[index] = (pixels[index] & 0xFE) | bit
    Image.frombytes("RGB", image.size, bytes(pixels)).save(output_path, format="PNG")


def extract(input_path: Path, password: str) -> str:
    image = Image.open(input_path).convert("RGB")
    pixels = bytes(image.tobytes())
    header = _read_bits(bytes(value & 1 for value in pixels), HEADER_SIZE * 8)
    if header[:4] != MAGIC:
        raise ValueError("No se encontró esteganografía STG1.")
    length = struct.unpack(">I", header[32:36])[0]
    total = HEADER_SIZE + length
    package = _read_bits(
        bytes(value & 1 for value in pixels[: total * 8]), total * 8
    )
    return decrypt(package, password)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    hide_parser = subparsers.add_parser("hide", help="Oculta un mensaje en PNG")
    hide_parser.add_argument("input", type=Path)
    hide_parser.add_argument("output", type=Path)
    hide_parser.add_argument("message")
    hide_parser.add_argument("password")

    extract_parser = subparsers.add_parser("extract", help="Extrae un mensaje de PNG")
    extract_parser.add_argument("input", type=Path)
    extract_parser.add_argument("password")
    args = parser.parse_args()

    if args.command == "hide":
        hide(args.input, args.output, args.message, args.password)
    else:
        print(extract(args.input, args.password))


if __name__ == "__main__":
    main()
