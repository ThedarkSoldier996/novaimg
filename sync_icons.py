import os
import json
import hashlib
import requests

from io import BytesIO
from PIL import Image

JSON_URL = "https://mrghnngupolsgatcmevw.supabase.co/storage/v1/object/public/Novaplay/novaplay.json"

ICON_DIR = "icons"

os.makedirs(ICON_DIR, exist_ok=True)

print("======================================")
print("       NOVAPLAY ICON SYNC")
print("======================================")

# Descargar JSON
print("Descargando novaplay.json...")

response = requests.get(JSON_URL, timeout=60)
response.raise_for_status()

data = response.json()

# Buscar todos los iconos
icon_urls = []


def extract_icons(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():

            if key == "icono":
                if (
                    isinstance(value, str)
                    and value.startswith(("http://", "https://"))
                ):
                    icon_urls.append(value)

            extract_icons(value)

    elif isinstance(obj, list):
        for item in obj:
            extract_icons(item)


extract_icons(data)

# Eliminar duplicados
icon_urls = list(dict.fromkeys(icon_urls))

print(f"Iconos encontrados: {len(icon_urls)}")

session = requests.Session()

successful = 0
failed = 0

index = []

for number, url in enumerate(icon_urls, start=1):

    try:
        print(f"[{number}/{len(icon_urls)}] {url}")

        # Hash estable basado en la URL
        url_hash = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()[:16]

        filename = f"{url_hash}.webp"

        output_path = os.path.join(
            ICON_DIR,
            filename
        )

        # Descargar
        image_response = session.get(
            url,
            timeout=60
        )

        image_response.raise_for_status()

        if not image_response.content:
            raise Exception("Imagen vacía")

        # Abrir imagen
        image = Image.open(
            BytesIO(image_response.content)
        )

        # Convertir a RGB/RGBA
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        # Guardar WebP
        image.save(
            output_path,
            "WEBP",
            quality=90,
            method=6
        )

        size_kb = os.path.getsize(output_path) / 1024

        print(
            f"  OK -> {filename} "
            f"({size_kb:.1f} KB)"
        )

        index.append({
            "icono": url,
            "archivo": filename
        })

        successful += 1

    except Exception as error:
        print(f"  ERROR -> {error}")
        failed += 1


# Crear índice
with open(
    os.path.join(ICON_DIR, "index.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        index,
        file,
        ensure_ascii=False,
        indent=2
    )


print()
print("======================================")
print("RESULTADO")
print("======================================")
print(f"Encontrados : {len(icon_urls)}")
print(f"Convertidos : {successful}")
print(f"Errores     : {failed}")
print("======================================")
