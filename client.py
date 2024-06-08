import paramiko
import logging
import os

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ip = '172.31.82.235'

def upload_file(client, file_path):
    try:
        ftp_conn = client.open_sftp()
        #destination_path = os.path.join('\\wsl.localhost', 'Ubuntu', 'sftpusers','admin')
        destination_path = os.path.join('local file')

        ftp_conn.put(file_path, destination_path)
        logging.info('File trasferito con successo a %s', destination_path)
        ftp_conn.close()
        return True
    except Exception as e:
        logging.error(f'Impossibile trasferire il file: {e}')
        return False

def main():
    client = paramiko.SSHClient()
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    client.load_host_keys(known_hosts_path)
    
    try:
        client.connect(ip, port=22, username='admin', password='admin')
    except paramiko.SSHException as e:
        logging.error(f"Errore di connessione SSH: {e}")
        return

    try:
        # Il canale aperto non è strettamente necessario per l'upload SFTP, quindi può essere omesso.
        upload_file(client, 'C:/Users/david/Desktop/script.txt')
    except Exception as e:
        logging.error(f"Errore durante l'operazione: {e}")
    finally:
        logging.info('Connessione chiusa')
        client.close()

if __name__ == "__main__":
    main()
