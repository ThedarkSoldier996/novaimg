```python
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


# ==================================================
# LEER NOVAPLAY.JSON
# ==================================================

print(
    f"Leyendo {JSON_FILE}...",
    flush=True
)

with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


print(
    "JSON cargado correctamente.",
    flush=True
)


# ==================================================
# BUSCAR CANALES
# ==================================================

channels = []


def extract_channels(obj):

    if isinstance(obj, dict):

        if (
            "canal" in obj
            and "icono" in obj
        ):

            canal = obj.get("canal")
            nombre = obj.get("name", "")
            icono = obj.get("icono")

            if (
                canal is not None
                and isinstance(icono, str)
                and icono.startswith(
                    ("http://", "https://")
                )
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


# ==================================================
# ELIMINAR DUPLICADOS DE CANAL
# ==================================================

unique = {}
duplicates = set()

for channel in channels:

    canal = channel["canal"]

    if canal in unique:

        duplicates.add(canal)

    else:

        unique[canal] = channel


channels = list(unique.values())


if duplicates:

    print(
        "Canales duplicados:",
        ", ".join(sorted(duplicates)),
        flush=True
    )


# ==================================================
# ORDENAR POR CANAL
# ==================================================

def sort_channel(channel):

    try:
        return int(channel["canal"])

    except ValueError:
        return 999999


channels.sort(
    key=sort_channel
)


# ==================================================
# DESCARGAR Y CONVERTIR
# ==================================================

session = requests.Session()

successful = 0
failed = 0

index = []


for channel in channels:

    canal = channel["canal"]
    name = channel["name"]
    url = channel["icono"]


    print("", flush=True)

    print(
        f"Canal {canal} - {name}",
        flush=True
    )


    try:

        # ------------------------------------------
        # Número del archivo
        # ------------------------------------------

        canal_number = int(canal)

        filename = (
            f"{canal_number:03d}.webp"
        )

        output_path = os.path.join(
            ICON_DIR,
            filename
        )


        print(
            f"Archivo: {filename}",
            flush=True
        )


        # ------------------------------------------
        # Descargar
        # ------------------------------------------

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

            raise Exception(
                "Imagen vacía"
            )


        # ------------------------------------------
        # Abrir imagen
        # ------------------------------------------

        image = Image.open(
            BytesIO(response.content)
        )

        image.load()


        # ------------------------------------------
        # Convertir
        # ------------------------------------------

        if image.mode in (
            "RGBA",
            "LA"
        ):

            image = image.convert(
                "RGBA"
            )

        else:

            image = image.convert(
                "RGB"
            )


        # ------------------------------------------
        # Guardar WebP
        # ------------------------------------------

        image.save(
            output_path,
            "WEBP",
            quality=90,
            method=6
        )


        size_kb = (
            os.path.getsize(
                output_path
            ) / 1024
        )


        print(
            f"OK -> {filename} "
            f"({size_kb:.1f} KB)",
            flush=True
        )


        # ------------------------------------------
        # Index
        # ------------------------------------------

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


# ==================================================
# CREAR INDEX.JSON
# ==================================================

index.sort(
    key=lambda x: int(x["canal"])
)


with open(
    os.path.join(
        ICON_DIR,
        "index.json"
    ),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        index,
        file,
        ensure_ascii=False,
        indent=2
    )


# ==================================================
# LIMPIAR ICONOS ANTIGUOS
# ==================================================

valid_files = {
    item["archivo"]
    for item in index
}


for filename in os.listdir(ICON_DIR):

    if (
        filename.endswith(".webp")
        and filename not in valid_files
    ):

        old_file = os.path.join(
            ICON_DIR,
            filename
        )

        os.remove(old_file)

        print(
            f"Eliminado antiguo: {filename}",
            flush=True
        )


# ==================================================
# RESULTADO
# ==================================================

print("", flush=True)

print(
    "======================================",
    flush=True
)

print(
    "             RESULTADO",
    flush=True
)

print(
    "======================================",
    flush=True
)

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

print(
    "======================================",
    flush=True
)
```
