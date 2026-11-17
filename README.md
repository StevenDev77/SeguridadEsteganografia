# Demostración de esteganografía

Este proyecto combina:

- **Cifrado:** AES-256-GCM protege el texto con una contraseña.
- **Esteganografía:** el texto cifrado se guarda en los bits menos
  significativos de una imagen PNG.
- **Video:** se usa un video MKV con códec FFV1 sin pérdida. La extracción se
  hace desde un fotograma PNG, porque MP4/H.264 puede destruir los bits ocultos.

## Estructura

```text
codigo/
  stego_demo.py
  generar_demo.py
  generar_medios_reales.py
medios/
  tierra_esteganografia.png
  astronauta_esteganografia.png
  astronauta_consola.mkv
```

## Decodificar la imagen de la Tierra

Desde la carpeta del proyecto:

```powershell
python codigo\stego_demo.py extract medios\tierra_esteganografia.png "Tierra-2026"
```

Resultado:

```text
Mensaje oculto en una fotografía real: la Tierra sigue siendo nuestro hogar.
```

## Decodificar la imagen del astronauta

```powershell
python codigo\stego_demo.py extract medios\astronauta_esteganografia.png "Astronauta-2026"
```

Resultado:

```text
Hackeado por estudiantes de software
```

## Decodificar el video

Primero extrae un fotograma sin recomprimirlo:

```powershell
ffmpeg -i medios\astronauta_consola.mkv -frames:v 1 medios\consola_001.png
python codigo\stego_demo.py extract medios\consola_001.png "Orion-2026"
```

Resultado:

```text
Hackeado por estudiantes de software
```

## Regenerar los medios

Requiere Python con `Pillow` y `cryptography`, además de `ffmpeg`:

```powershell
python codigo\generar_medios_reales.py
```

Las imágenes fuente son fotografías de NASA obtenidas desde NASA Images y
Wikimedia Commons. Comprueba las condiciones de atribución antes de publicar
los archivos.

Las contraseñas incluidas son únicamente de demostración; no las uses para
proteger información real.
