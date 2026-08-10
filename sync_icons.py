import os
import json
import requests

from io import BytesIO
from PIL import Image


JSON_FILE = "novaplay.json"
ICON_DIR = "icons"

os.makedirs(ICON_DIR, exist_ok=True)

print("======================================", flush=True)
print("       NOVAPLAY ICON SYNC", flush=True)
print("======================================", flush=True)


# Leer novaplay.json
print("Leyendo novaplay.json...", flush=True)

with open(JSON_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

print("JSON cargado correctamente.", flush=True)


# Buscar canales
channels = []


def extract_channels(obj):

    if isinstance(obj, dict):

        if "canal" in obj and "icono" in obj:

            canal = obj.get("canal")
            nombre = obj.get("name", "")
            icono = obj.get("icono")

            if (
                canal is not None
                and isinstance(icono, str)
                and icono.startswith(("http://", "https://"))
            ):
                channels.append({
                    "canal": str(canal),
                    "name": str(nombre),
                    "icono": icono
                })

        for value in obj.values():
            extract_channels(value)

    elif isinstance(obj, list):

        for item in obj:
            extract_channels(item)


extract_channels(data)

print(
    f"Canales encontrados: {len(channels)}",
    flush=True
)


# Eliminar canales duplicados
unique_channels = {}

for channel in channels:

    canal = channel["canal"]

    if canal not in unique_channels:
        unique_channels[canal] = channel


channels = list(unique_channels.values())


# Ordenar por número de canal
def sort_channel(channel):

    try:
        return int(channel["canal"])
    except ValueError:
        return 999999


channels.sort(key=sort_channel)


# Descargar y convertir
session = requests.Session()

successful = 0
failed = 0

index = []


for channel in channels:

    canal = channel["canal"]
    name = channel["name"]
    url = channel["icono"]

    print("", flush=True)
    print(f"Canal: {canal}", flush=True)
    print(f"Nombre: {name}", flush=True)
    print(f"URL: {url}", flush=True)

    try:

        canal_number = int(canal)

        # Canal 1 = 001.webp
        # Canal 25 = 025.webp
        # Canal 100 = 100.webp
        filename = f"{canal_number:03d}.webp"

        output_path = os.path.join(
            ICON_DIR,
            filename
        )

        print(
            f"Archivo: {filename}",
            flush=True
        )

        print(
            "Descargando...",
            flush=True
        )

        response = session.get(
            url,
            timeout=(15, 60)
        )

        response.raise_for_status()

        if not response.content:
            raise Exception("Imagen vacía")

        print(
            f"Descargado: "
            f"{len(response.content) / 1024:.1f} KB",
            flush=True
        )

        # Abrir imagen
        image = Image.open(
            BytesIO(response.content)
        )

        image.load()

        # Convertir
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        # Guardar WebP
        print(
            "Convirtiendo a WebP...",
            flush=True
        )

        image.save(
            output_path,
            "WEBP",
            quality=90,
            method=6
        )

        size_kb = (
            os.path.getsize(output_path) / 1024
        )

        print(
            f"OK -> {filename} "
            f"({size_kb:.1f} KB)",
            flush=True
        )

        index.append({
            "canal": canal,
            "name": name,
            "icono": url,
            "archivo": filename
        })

        successful += 1

    except Exception as error:

        print(
            f"ERROR: {error}",
            flush=True
        )

        failed += 1


# Ordenar index.json por canal
index.sort(
    key=lambda item: int(item["canal"])
)


# Guardar index.json
print("", flush=True)
print("Generando index.json...", flush=True)

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


# Eliminar WebP de canales que ya no existen
valid_files = {
    item["archivo"]
    for item in index
}


for filename in os.listdir(ICON_DIR):

    if (
        filename.endswith(".webp")
        and filename not in valid_files
    ):

        path = os.path.join(
            ICON_DIR,
            filename
        )

        os.remove(path)

        print(
            f"Eliminado: {filename}",
            flush=True
        )


# Resultado
print("", flush=True)
print("======================================", flush=True)
print("             RESULTADO", flush=True)
print("======================================", flush=True)
print(
    f"Canales encontrados : {len(channels)}",
    flush=True
)
print(
    f"Convertidos         : {successful}",
    flush=True
)
print(
    f"Errores             : {failed}",
    flush=True
)
print("======================================", flush=True)
