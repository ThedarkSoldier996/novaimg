import os
import json
import requests

from io import BytesIO
from PIL import Image


JSON_FILE = "novaplay.json"
ICON_DIR = "icons"

GITHUB_BASE_URL = (
    "https://raw.githubusercontent.com/"
    "ThedarkSoldier996/novaimg/main/icons/"
)

os.makedirs(ICON_DIR, exist_ok=True)

print("======================================", flush=True)
print("       NOVAPLAY ICON SYNC", flush=True)
print("======================================", flush=True)


# ==================================================
# LEER JSON
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
# PROCESAR CATEGORIAS Y CANALES
# ==================================================

channels = []


def process_structure(obj):

    if isinstance(obj, list):

        for item in obj:

            process_structure(item)


    elif isinstance(obj, dict):

        # Si tiene items, recorrerlos
        if isinstance(obj.get("items"), list):

            for item in obj["items"]:

                # Si parece un canal
                if (
                    isinstance(item, dict)
                    and "name" in item
                ):

                    channels.append(item)

                # También puede ser otra estructura
                else:

                    process_structure(item)

        else:

            # Buscar estructuras internas
            for value in obj.values():

                if isinstance(value, (dict, list)):

                    process_structure(value)


process_structure(data)


print(
    f"Canales encontrados: {len(channels)}",
    flush=True
)


# ==================================================
# DESCARGAR ICONOS
# ==================================================

session = requests.Session()

successful = 0
failed = 0

index = []


for position, channel in enumerate(
    channels,
    start=1
):

    name = str(
        channel.get("name", "")
    )

    icon_url = channel.get("icono")

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


    # ----------------------------------------------
    # Sin icono
    # ----------------------------------------------

    if not isinstance(
        icon_url,
        str
    ) or not icon_url.startswith(
        ("http://", "https://")
    ):

        print(
            "Sin URL de icono. Se mantiene sin cambios.",
            flush=True
        )

        index.append({
            "numero": position,
            "name": name,
            "icono_original": icon_url,
            "archivo": None
        })

        continue


    print(
        f"Origen: {icon_url}",
        flush=True
    )

    print(
        f"Destino: {filename}",
        flush=True
    )


    try:

        # ------------------------------------------
        # Descargar imagen original
        # ------------------------------------------

        response = session.get(
            icon_url,
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
        # Convertir a WebP
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


        print(
            f"OK -> {filename}",
            flush=True
        )


        # ------------------------------------------
        # URL nueva de GitHub
        # ------------------------------------------

        github_url = (
            GITHUB_BASE_URL
            + filename
        )


        # IMPORTANTE:
        # Solo reemplazamos icono.
        channel["icono"] = github_url


        index.append({
            "numero": position,
            "name": name,
            "icono": github_url,
            "archivo": filename,
            "icono_original": icon_url
        })


        successful += 1


    except Exception as error:

        print(
            f"ERROR: {error}",
            flush=True
        )

        # Si falla la descarga,
        # NO reemplazamos el icono original.

        index.append({
            "numero": position,
            "name": name,
            "icono": icon_url,
            "archivo": None
        })

        failed += 1


# ==================================================
# GUARDAR NOVAPLAY.JSON
# ==================================================

print("", flush=True)

print(
    "Actualizando únicamente los campos icono...",
    flush=True
)


with open(
    JSON_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )

    file.write("\n")


print(
    "novaplay.json actualizado.",
    flush=True
)


# ==================================================
# GUARDAR INDEX.JSON
# ==================================================

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

    file.write("\n")


# ==================================================
# ELIMINAR WEBP SOBRANTES
# ==================================================

valid_files = {
    item["archivo"]
    for item in index
    if item["archivo"]
}


for filename in os.listdir(ICON_DIR):

    if (
        filename.endswith(".webp")
        and filename not in valid_files
    ):

        os.remove(
            os.path.join(
                ICON_DIR,
                filename
            )
        )

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
    f"Iconos convertidos  : {successful}",
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
