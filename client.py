import paramiko
import logging
import socket
import os

def main():
    client = paramiko.SSHClient()
    known_hosts_path = os.path.join(os.environ['USERPROFILE'], '.ssh', 'known_hosts')
    client.load_host_keys(known_hosts_path)

    try:
        client.connect('192.168.159.139', port=2200, username='rans', password='password')
    except paramiko.SSHException as e:
        print(f"Errore di connessione: {e}")
        return

    try:
        channel = client.get_transport().open_session()
    except paramiko.SSHException as e:
        print(f"Errore durante l'apertura del canale: {e}")
        return

    try:
        while True:
            command = input("Inserisci il comando da eseguire: ")
            channel.send(command)

            output = ""
            logging.info('In attesa di dati dal server...')
            while True:
                data = channel.recv(1024).decode()
                print(data)
                if not data:
                    break
                output += data 
            print(output)

    except paramiko.SSHException as e:
        if "closed by remote host" in str(e):
            print("Connessione chiusa dal server.")
        else:
            logging.error(e)
    finally:
        channel.close()
        client.close()
        logging.info('Connessione chiusa.')

if __name__ == "__main__":
    main()
