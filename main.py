import tkinter as tk
from time import sleep
import json
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import os
from pathlib import Path
import requests
import base64
import shutil
import json

def check_token():
    global token

    with open("configs/config.json", "r") as file:
        data = json.load(file)
    token = data.get("token")

    # TODO: adicionar uma verificacao se o token é valido ou nao, e pedir para inserir novamente
    if not data["token"]:
        # Função chamada quando o botão é pressionado
        def exibir_texto():
            token_var = campo_texto.get()
            rotulo.config(text=f"Token adicionado!")
            sleep(2)
            data["token"] = token_var

            with open("configs/config.json", "w") as file:
                json.dump(data, file)
            quit()

        # Cria uma instância da janela
        check = tk.Tk()

        # Define o título da janela
        check.title("Minha Aplicação Tkinter")

        # Define as dimensões da janela (largura x altura)
        check.geometry("400x300")

        # Cria um rótulo na janela
        rotulo = tk.Label(check, text="Adicione seu token do ImgBB:")
        rotulo.pack()

        # Cria um campo de entrada na janela
        campo_texto = tk.Entry(check)
        campo_texto.pack()

        # Cria um botão na janela
        botao = tk.Button(check, text="Exibir", command=exibir_texto)
        botao.pack()

        # Inicia o loop principal da interface gráfica
        check.mainloop()
       
    else:
        # Configuração da janela principal
        janela = TkinterDnD.Tk()
        janela.title("Gerador de Links")

        # Defina as dimensões da janela para 400x300 pixels
        janela.geometry("400x300")

        # Cria um rótulo na janela
        label = tk.Label(janela, text="Arraste e solte os arquivos na interface", height=200, font="Helvetica")
        label.pack()

        # Cria um rótulo para exibir o nome do arquivo
        label_arquivo = tk.Label(janela, text="")
        label_arquivo.pack()

        # Adicione a funcionalidade de arrastar e soltar
        janela.drop_target_register(DND_FILES)
        janela.dnd_bind('<<Drop>>', handle_drop)

        # Inicia o loop principal da interface gráfica
        janela.mainloop()
        
        
def handle_drop(event):
    global files
    files = event.widget.tk.splitlist(event.data)
    convert_images()
    upload_images()


def convert_images():
    for filename in files:
        file_abs_path = filename
        filename = filename[3:]
        
        if os.path.isdir(file_abs_path):
            os.mkdir(path=f"converted/{filename}")
            for file in os.listdir(file_abs_path):
                
                name, ext = os.path.splitext(file)
                print(name, ext)
                
                if ext != ".png":
                    img = Image.open(f"{file_abs_path}/{file}").convert("RGB")
                    img.save(f"converted/{filename}/{name}.jpeg")
                else:
                    img = Image.open(f"{file_abs_path}/{file}").convert("RGBA")
                    img.save(f"converted/{filename}/{name}.png")
        
        if os.path.isfile(file_abs_path):
            filename = os.path.basename(filename)
            name, ext = os.path.splitext(filename)
            if ext != ".png":
                if not os.path.exists("converted/default"):
                    os.mkdir(path=f"converted/default")
                img = Image.open(file_abs_path).convert("RGB")
                img.save(f"converted/default/{name}.jpeg")
            else:
                if not os.path.exists("converted/default"):
                    os.mkdir(path=f"converted/default")
                img = Image.open(file_abs_path).convert("RGBA")
                img.save(f"converted/default/{name}.png")


def upload_images():
    for folder in os.listdir("converted"):
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


check_token()


