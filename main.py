#!/usr/bin/env python3 

import requests
import io
import hashlib
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv





dotenv_path = os.path.join(os.path.dirname(__file__), '.env')


if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    BASE_URL = os.environ.get("BASE_URL")
    BUF_SIZE = int(os.environ.get("BUF_SIZE"))
    url = os.environ.get("url")
    token = os.environ.get("token")
    ids = os.environ.get("ids").split(',')
    filename = os.environ.get("filename")
    hashfilename = os.environ.get("hashfilename")
    group = os.environ.get("group")

file_buffer= io.BytesIO()
filename = dotenv_path = os.path.join(os.path.dirname(__file__), filename)
file_buffer.name=filename

def checkfile(file):
    isExists = os.path.exists(file) 
    print(f"[+] Файл {file} существует: {isExists}")
    return isExists



def getPage(url):
    r = requests.get(url)
    if r.status_code == 200:
        src = r.text
    else:
        print(f"Ошибка сети {r.status_code}")
    return(src)

def parsePage(page):
    text = ''
    url = ''
    soup = BeautifulSoup(page, "lxml")
    page_all_a=soup.find_all("a")
    for i in page_all_a:
        url=i.get("href")
        text=i.text
        if text == group:
            print(f"[+] {text}  {url}")
            return url
    

def downloadFile(url):
    url = BASE_URL + url
    response = requests.get(url)
    print(f"[+] Найден файл  {url}")
    file_buffer.write(response.content)
    file_buffer.seek(0)
    print(f"[+] Загружен файл inmemory_mod:: {file_buffer.name}")
    return file_buffer


def getFileHash(file):
    with open(hashlib.__file__, "rb") as filebuffer:
        digest = hashlib.file_digest(filebuffer, "sha256")
        filebuffer.seek(0)

    sha256hex=digest.hexdigest()
        
    print(f"[+] SHA256 = {sha256hex}")
    return sha256hex

def writeHash(hash):
    with open(hashfilename, mode="w") as file:
        file.write(hash)
 
    print(f"[+] Записан файл {hashfilename}")

def readHashFromFile(file):
    with open(file, mode="r") as f:
        hash = f.readline()
    print(f"[+] SHA256 = {hash}")
    return hash


def sendFile(chatid,file):
    print(f"[+] Отправляю файл {file.name}")
    
    data = {
        'chat_id': (None, chatid),
        'document':('shedule.pdf',io.BufferedReader(io.BytesIO(file.read())))
        }
    try:
        response = requests.post(f'https://api.telegram.org/bot{token}/sendDocument', files=data)
        print(f"[+] Файл {file.name} отправлен {chatid}")
    except Exception as e:
        print(e)

def sendMessage(chatid,message):
    data = {
        'chat_id': chatid,
        'text': message
    }
    
    try:
        response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json=data)
        
    except Exception as e:
        print(e)

def sendFileToEverybody(file):
    for chatid in ids:
        sendMessage(chatid,'Новое расписание!')
        sendFile(chatid,file)




if __name__ == "__main__":
    if checkfile(hashfilename):
        print(f"[+] Хэш текущего расписания")
        old_hash=readHashFromFile(hashfilename)
        print(f"[+] Поиск и загрузка нового расписания")
        buffer=downloadFile(parsePage(getPage(url)))
        print(f"[+] Хэш нового расписания")
        new_hash=getFileHash(buffer)
        if old_hash != new_hash:
            print("[+] Новое расписание")
            sendFileToEverybody()
            writeHash(new_hash)
        else:
            print(f"[+] old_hash = {old_hash} \n[+] new_hash = {new_hash}")
            print(f"[+] Хэш файлы совпадают")
            print(f"[+] Расписание не изменилось")
    else:
        print(f"[+] Поиск и загрузка нового расписания")
        buffer=downloadFile(parsePage(getPage(url)))
        print(f"[+] Хэш нового расписания")
        hash=getFileHash(buffer)
        writeHash(hash)
        print("[+] Новое расписание")
        sendFileToEverybody(buffer)
        
    print(f"[+] Выход")
        
    