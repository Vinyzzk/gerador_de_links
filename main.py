import os
import shutil
from tqdm import tqdm  # progress bar
from PIL import Image
import requests
import base64
import json
import openpyxl
import pandas as pd


def clear_folder(folder):
    helper = 0
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"[!] Pasta \"{folder}\" resetada")

        if os.path.isfile(file_path):
            os.remove(file_path)
            helper += 1

    if helper >= 1:
        print(f"[!] Pasta \"{folder}\" resetada")


def check_default_folders():
    error_empty_folder = 0
    default_folders = ["images", "converted"]
    folders_created = 0
    for folder in default_folders:
        try:
            os.mkdir(f"{folder}")
            print(f"[+] Pasta {folder} criada")
            folders_created += 1
        except FileExistsError:
            error_empty_folder = 1
            continue

    if folders_created > 0:
        quit()

    if error_empty_folder == 1:
        files = os.listdir("images")
        if len(files) == 0:
            print(f'[!] É preciso adicionar imagens em "images"')
            input(f"Pressione ENTER para sair")
            quit()


# Destroi o arquivo "desktop.ini"
def check_desktop_ini():
    folder = "images"
    for file in os.listdir(folder):
        path = os.path.abspath(os.path.join(folder, file))
        if os.path.isdir(path):
            for image in os.listdir(path):
                name, ext = os.path.splitext(image)
                if ext == ".ini":
                    file_path = os.path.abspath(os.path.join(path, image))
                    os.remove(file_path)
                    print("[!] Um arquivo .ini destruído com sucesso")
        if os.path.isfile(path):
            name, ext = os.path.splitext(file)
            if ext == ".ini":
                file_path = os.path.abspath(os.path.join(folder, file))
                os.remove(file_path)
                print("[!] Um arquivo .ini destruído com sucesso")


def check_token():
    global token

    with open("configs/config.json", "r") as file:
        data = json.load(file)
    token = data.get("token")

    # TODO: adicionar uma verificacao se o token é valido ou nao, e pedir para inserir novamente
    if not data["token"]:
        data["token"] = str(input("Adicione seu token do ImgBB: "))
        print(f"[+] Token adicionado")

        with open("configs/config.json", "w") as file:
            json.dump(data, file)
        input(f"Pressione ENTER para sair")
        quit()


def convert_images():
    print(f"[+] Convertendo imagens")
    for filename in tqdm(os.listdir("images")):
        file_path = os.path.join("images", filename)
        if os.path.isdir(file_path):
            os.mkdir(path=f"converted/{filename}")
            for file in os.listdir(f"images/{filename}"):
                name, ext = os.path.splitext(file)
                if ext != ".png":
                    img = Image.open(f"images/{filename}/{file}").convert("RGB")
                    img.save(f"converted/{filename}/{name}.jpeg")
                else:
                    img = Image.open(f"images/{filename}/{file}").convert("RGBA")
                    img.save(f"converted/{filename}/{name}.png")
        else:
            name, ext = os.path.splitext(filename)
            if ext != ".png":
                if not os.path.exists("converted/default"):
                    os.mkdir(path=f"converted/default")
                img = Image.open(f"images/{filename}").convert("RGB")
                img.save(f"converted/default/{name}.jpeg")
            else:
                if not os.path.exists("converted/default"):
                    os.mkdir(path=f"converted/default")
                img = Image.open(f"images/{filename}").convert("RGBA")
                img.save(f"converted/default/{name}.png")


def upload_images():
    print(f"[+] Upando imagens")
    for folder in tqdm(os.listdir("converted")):
        links = []
        links_bling = []
        links_bling_com_sku = [f"{folder}"]
        links_bling_excel = []
        for img in os.listdir(f"converted/{folder}"):
            name, ext = os.path.splitext(img)
            if not img.endswith(".txt"):
                with open(f"converted/{folder}/{img}", "rb") as file:
                    url = "https://api.imgbb.com/1/upload"
                    payload = {
                        "key": f"{token}",
                        "image": base64.b64encode(file.read()),
                    }
                    res = requests.post(url, payload)
                    res = res.json()
                    res = res.get("data")
                    res = res.get("url")
                    links.append(f"{name}|{res}\n")
                    links_bling.append(f"{res}")
                    links_bling_com_sku.append(f"{res}")
                    links_bling_excel.append(f"{res}")

        my_separator = "|"
        links.sort()  # Ordenar os links em ordem alfabética
        links_bling = my_separator.join(links_bling)  # Separar os links com o separador definido
        links_bling_com_sku = my_separator.join(
            links_bling_com_sku)  # Separar os links com SKU com o separador definido
        links_bling_excel = my_separator.join(
            links_bling_excel)  # Separar os links com SKU com o separador definido
        with open(f"converted/{folder}/url.txt", "w+") as txt:
            txt.writelines(links)
        with open(f"converted/{folder}/url_bling.txt", "w+") as txt2:
            txt2.writelines(links_bling)

    line()


def generate_excel():
    data = []
    for folder in os.listdir("converted"):
        for file in os.listdir(f"converted/{folder}"):
            if file == "url_bling.txt":
                with open(f"converted/{folder}/{file}", "r") as txt:
                    for item in txt:
                        data.append({'SKU': folder, 'Links': item})

    df = pd.DataFrame(data)
    df.to_excel("result.xlsx", index=False, engine="openpyxl")


# Função auxiliar para imprimir uma linha separadora
def line():
    print("------------------------------------------")


if __name__ == "__main__":
    # Basic checks
    check_token()
    check_default_folders()
    check_desktop_ini()

    clear_folder("converted")

    line()

    convert_images()

    upload_images()
    clear_folder("images")

    generate_excel()

    input(f"Pressione ENTER para sair")


