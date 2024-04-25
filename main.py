import tkinter as tk
from tkinter import messagebox
from time import sleep
import json
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
from pathlib import Path
import requests
import base64
import shutil
import json
import pandas as pd
import openpyxl


root = TkinterDnD.Tk()
root.title(f"Gerador de Links | {os.getlogin()} <> vinicius@echodata")
root.geometry("500x250")
root.iconbitmap("isotipo_echodata_M5v_icon.ico")

def check_token():
    global token

    with open("configs/config.json", "r") as file:
        data = json.load(file)
    token = data.get("token")

    # TODO: adicionar uma verificacao se o token é valido ou nao, e pedir para inserir novamente
    # TODO: adicionaru um botao para readicionar o token
    # TODO: adicionar logs terminal-based, e retorno de interface de usuario conforme os arquivos forem sendo convertidos e upados
    if not data["token"]:
        def add_token():
            token_var = campo_texto.get()
            if len(token_var) < 30:
                rotulo.config(text=f"Token invalido")
            else:
                rotulo.config(text=f"Token adicionado!")
                sleep(2)
                data["token"] = token_var

                with open("configs/config.json", "w") as file:
                    json.dump(data, file)
                    
                rotulo.destroy()
                campo_texto.destroy()
                botao.destroy()
                generator()

        def trigger_add(event):
            add_token()

        # Use a janela principal criada fora da função
        rotulo = tk.Label(root, text="Adicione seu token do ImgBB:", font="Helvetica")
        rotulo.pack()

        campo_texto = tk.Entry(root)
        campo_texto.pack()
        
        botao = tk.Button(root, text="Adicionar", command=add_token)
        botao.pack()
        
        campo_texto.bind("<Return>", trigger_add)
        
    else:
        generator()

       
def check_default_folders():
    try:
        os.mkdir("converted")
        print("[+] Folder \"converted\" have been created")
    except FileExistsError:
        print("[+] Folder \"converted\" already exists")
    
       
def generator():
    label = tk.Label(root, text="Arraste e solte os arquivos na interface", height=200, font="Helvetica")
    label.pack()

    label_arquivo = tk.Label(root, text="")
    label_arquivo.pack()

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', handle_drop)
        
        
def handle_drop(event):
    global files
    files = event.widget.tk.splitlist(event.data)
    convert_images()
    upload_images()


def convert_images():
    for filename in files:
        file_abs_path = filename
        last_folder_name = os.path.basename(os.path.normpath(file_abs_path))
        print(last_folder_name)
        if os.path.isdir(file_abs_path):
            os.mkdir(os.path.join("converted", last_folder_name))
            for file in os.listdir(file_abs_path):
                name, ext = os.path.splitext(file)
                print(name, ext)
                
                if ext != ".png":
                    img = Image.open(f"{file_abs_path}/{file}").convert("RGB")
                    img.save(f"converted/{last_folder_name}/{name}.jpeg")
                else:
                    img = Image.open(f"{file_abs_path}/{file}").convert("RGBA")
                    img.save(f"converted/{last_folder_name}/{name}.png")
        
        if os.path.isfile(file_abs_path):
            filename = os.path.basename(filename)
            name, ext = os.path.splitext(filename)
            if ext == ".ini":
                os.remove(file_abs_path)
                print("[!] Um arquivo .ini destruído com sucesso")
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
    data = []

    for folder in os.listdir("converted"):
        links = []
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
                    links.append(f"{res}\n")
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

 
        data.append({"SKU": folder, "Links": links_bling_excel})

    df = pd.DataFrame(data)
    df.to_excel("converted/result.xlsx", index=False, engine="openpyxl")

    messagebox.showinfo("Alerta", "Imagens upadas")


if __name__ == "__main__":
    check_default_folders()
    check_token()
    root.mainloop()  # Inicie o loop principal do Tkinter
