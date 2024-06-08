import paramiko
import logging
import os

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sysRoot = os.path.expanduser('~')

log_path = f"{sysRoot}\\Documents\\log_file.txt"


ip = '192.168.159.139'

def read_log():
    paths = []
    with open(log_path, 'r') as f:
        for line in f:
            paths.append(line.strip())
    return paths


def main():
    client = paramiko.SSHClient()
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    client.load_host_keys(known_hosts_path)
    try: 
        client.connect(ip, port=22, username='admin', password='admin')
        ftp_conn = client.open_sftp()
        paths = read_log()
        for path in paths:
        # Il canale aperto non è strettamente necessario per l'upload SFTP, quindi può essere omesso.
            ftp_conn.put(path, remotepath=os.path.basename(path))
            logging.info('File trasferito con successo a %s')
           
    except Exception as e:
        logging.error(f'Impossibile trasferire il file: {e}')
       
    finally:
        ftp_conn.close()
        logging.info('Connessione chiusa')
        client.close()

if __name__ == "__main__":
    main()
