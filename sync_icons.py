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

print("Leyendo novaplay.json...", flush=True)

with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

print("JSON cargado correctamente.", flush=True)


# ==================================================
# BUSCAR CANALES CON ICONO
# ==================================================

channels = []


def extract_channels(obj):

    if isinstance(obj, dict):

        # Canal que contiene icono
        if "icono" in obj:

            icono = obj.get("icono")

            if (
                isinstance(icono, str)
                and icono.startswith(
                    ("http://", "https://")
                )
            ):

                channels.append({
                    "name": str(
                        obj.get("name", "")
                    ),
                    "icono": icono
                })

        # Continuar recorriendo
        for value in obj.values():
            extract_channels(value)


    elif isinstance(obj, list):

        for item in obj:
            extract_channels(item)


extract_channels(data)


print(
    f"Iconos encontrados: {len(channels)}",
    flush=True
)


# ==================================================
# DESCARGAR ICONOS EN EL MISMO ORDEN
# ==================================================

session = requests.Session()

successful = 0
failed = 0

index = []


for position, channel in enumerate(
    channels,
    start=1
):

    name = channel["name"]
    url = channel["icono"]

    # El número depende EXCLUSIVAMENTE
    # de la posición dentro del JSON.
    filename = f"{position:03d}.webp"

    output_path = os.path.join(
        ICON_DIR,
        filename
    )


    print("", flush=True)

    print(
        f"[{position}/{len(channels)}] {name}",
        flush=True
    )

    print(
        f"URL: {url}",
        flush=True
    )

    print(
        f"Archivo: {filename}",
        flush=True
    )


    try:

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
        # Guardar información
        # ------------------------------------------

        index.append({
            "numero": position,
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
# GUARDAR INDEX.JSON
# ==================================================

print("", flush=True)

print(
    "Generando index.json...",
    flush=True
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
# ELIMINAR ICONOS SOBRANTES
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

        path = os.path.join(
            ICON_DIR,
            filename
        )

        os.remove(path)

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
    f"Iconos encontrados : {len(channels)}",
    flush=True
)

print(
    f"Convertidos        : {successful}",
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
