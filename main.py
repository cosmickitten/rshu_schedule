import requests
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
    group = os.environ.get("group")


def checkfile():
    isExists = os.path.exists(filename) 
    print(f"[+] Файл {filename} существует: {isExists}")
    return isExists

def hashfile():
    
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:      
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    sha256hex =  sha256.hexdigest()
    print(f"[+] SHA256 = {sha256hex}")
    return sha256hex
 



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
    with open(filename, mode="wb") as file:
        file.write(response.content)
    print(f"[+] Загружен файл {filename}")



def sendFile(chatid):
    print(f"[+] Отправляю файл {filename}")
    
    files = {
        'chat_id': (None, chatid),
        'document': open(filename, 'rb')
        }

    response = requests.post(f'https://api.telegram.org/bot{token}/sendDocument', files=files)
    print(f"[+] Файл {filename} отправлен {chatid}")


def sendFileToEverybody():
    for chatid in ids:
        sendFile(chatid)


if __name__ == "__main__":
    if checkfile():
        old=hashfile()
        downloadFile(parsePage(getPage(url)))
        new=hashfile()
        if old != new:
            print("[+] Новое рассписание")
            sendFileToEverybody()
    else:
        downloadFile(parsePage(getPage(url)))
        sendFileToEverybody()
    