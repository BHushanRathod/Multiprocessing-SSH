import sys
import time
import base64
from io import StringIO
import multiprocessing
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import paramiko
import psycopg2


def cipher_fernet(password):
    """
    fernet object for encrypting and decrypting the file
    :param password:
    :return:
    """
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"abcd",
        iterations=10,
        backend=default_backend(),
    ).derive(password)
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt1(plaintext, password):
    """
    Method to create the fernet encrypt object the file with given password
    :param plaintext:
    :param password:
    :return:
    """
    return cipher_fernet(password).encrypt(plaintext)


def decrypt1(ciphertext, password):
    """
    Method to create the fernet decrypt object the file provided the password
    :param ciphertext:
    :param password:
    :return:
    """
    return cipher_fernet(password).decrypt(ciphertext)


def decrypt_file(ctext):
    """
    Method to decrypt the file provided the password
    :param ctext:
    :return:
    """
    passphrase = input("Enter PassPhrase to deccrypt private key: ").encode()
    try:
        key = decrypt1(ctext.encode(), passphrase)
        return key.decode()
    except InvalidToken:
        print("Wrong PassPhrase")
        sys.exit()


def insert_key():
    """
    Method to encrypt the file with given password
    :return:
    """
    print("Enter file location like >> path/to/file/<filename>.pem")
    location = input("Please enter the key location: ")
    try:
        with open(location, "r") as file:
            data = file.read()
            passphrase = input("Enter passphrase to encrypt: ")
            print("Store the passphrase at secure location")
            time.sleep(2)
            ctext = encrypt1(data.encode(), passphrase.encode())
            cur, conn = connect_to_postres()
            cur.execute("select * from key_vals")
            rows = cur.fetchall()
            if not rows:
                cur.execute("INSERT INTO key_vals DEFAULT VALUES")
            key = "'" + ctext.decode() + "'"
            cur.execute("update key_vals set key=" + key + ";")
            conn.commit()
            print("New key updated in database")
            time.sleep(3)
            conn.close()
    except FileNotFoundError as e:
        print("No file found. Please check the file path.")
        print("path/to/file/<filename>.pem")
        time.sleep(4)


def read_private_key(data):
    """
    Read the RSA file with paramiko
    :param data:
    :return:
    """
    return paramiko.RSAKey.from_private_key(StringIO(data))


def execute_cmd(ssh, cmd):
    """
    Method to excute the command in an instance
    :param ssh:
    :param cmd:
    :return:
    """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    outlines = stdout.readlines()
    response = "".join(outlines)
    return response


def get_hostnames():
    """
    Read the file hostname_list.text and get all the hostnames
    :return:
    """
    with open("hostname_list.txt", "r") as file:
        data = file.readlines()
        return [line.rstrip() for line in data if line.strip()]


def connect_to_instance(hostname, key, user):
    """
    Method to connect to instance using private key and user
    :param hostname:
    :param key:
    :param user:
    :return:
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, username=user, pkey=key)
        host_name = execute_cmd(ssh, "hostname")
        cpu_cnt = execute_cmd(ssh, "nproc")
        print(
            "Connected to IP: {} \n Hostname: {} and CPU cores are {} ".format(
                hostname, host_name, cpu_cnt
            )
        )
        ssh.close()
        print("SSH Connection Closed: ", hostname)
        print("~" *50)
    except:
        print("Error connecting: ", hostname)
        ssh.close()


def get_privatekey():
    """
    Method to get the key from database
    :return:
    """
    cur, conn = connect_to_postres()
    cur.execute("select * from key_vals")
    rows = cur.fetchall()
    key = None
    for row in rows:
        key = row[1]
    conn.close()
    return key


def connect_to_postres():
    """
    Connect to the PostgreSQL database server
    :return:
    """

    try:
        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="admin",
            host="127.0.0.1",
            port="5432",
        )

        # create a cursor
        cur = conn.cursor()
        return cur, conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def main():
    """
    Main Method
    :return:
    """
    host_list = get_hostnames()
    enc_key = get_privatekey()
    data = read_private_key(decrypt_file(enc_key))

    procs = []

    for name in host_list:
        proc = multiprocessing.Process(
            target=connect_to_instance, args=(name, data, "ubuntu")
        )
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print("Done")
    time.sleep(1)


if __name__ == "__main__":
    while True:
        print("""
                    Multiprocessing SSH
        Program read the hostname_list.txt file.
        Insert the key in postgres database.
            a. To insert the key into postgres, create a 'key_vals' table with column (hostname, key, user_name).
            b. To insert private into table, Select option 1.
        -----------------------------------------------------""")

        option = input("""
        1. Insert private key in database
        2. Connect to instance to get information.
        Q. Exit the program
        Enter the option: """)
        if option == '1':
            print("Inserting the new key into database. It'll overwrite any old key.")
            time.sleep(2)
            insert_key()
        elif option == '2':
            print("Program will now SSH into each host, will pring hostname and CPU Cores.")
            time.sleep(2)
            main()
            sys.exit()
        elif option.lower() == 'q':
            print("__Existing__")
            time.sleep(1)
            sys.exit()
        else:
            sys.exit()
