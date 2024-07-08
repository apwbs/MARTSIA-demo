import socket
import ssl
from decouple import config
from hashlib import sha512
import sqlite3
import argparse

# Connection to SQLite3 reader database
connection = sqlite3.connect('../databases/reader/reader.db')
x = connection.cursor()


def sign_number(authority_invoked):
    x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), authority_invoked))
    result = x.fetchall()
    number_to_sign = result[0][2]

    x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = x.fetchall()
    private_key = result[0]

    private_key_n = int(private_key[1])
    private_key_d = int(private_key[2])

    msg = bytes(str(number_to_sign), 'utf-8')
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, private_key_d, private_key_n)
    # print("Signature:", hex(signature))
    return signature


"""
function to handle the sending and receiving messages.
"""


def receive_message():
    message = ""
    while True:
        data = conn.recv(1024).decode(FORMAT)
        if not data:  # No data received
            break
        message += data
        return message


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (int(HEADER) - len(send_length))
    conn.send(send_length)
    # print(send_length)
    conn.send(message)
    receive = receive_message()
    if len(receive) != 0:
        if receive.startswith('number to sign:'):
            x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?)",
                      (str(process_instance_id), authority, receive[16:]))
            connection.commit()
            return True
        #     x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?)",
        #               (process_instance_id, authority, receive[16:]))
        #     connection.commit()
        x.execute("INSERT OR IGNORE INTO authorities_generated_decription_keys VALUES (?,?,?)",
                  (str(process_instance_id), authority, receive))
        connection.commit()


process_instance_id_env = config('PROCESS_INSTANCE_ID')
process_instance_id = int(process_instance_id_env)

HEADER = config('HEADER')
FORMAT = 'utf-8'
server_sni_hostname = config('SERVER_SNI_HOSTNAME')
DISCONNECT_MESSAGE = "!DISCONNECT"
server_cert = '../Keys/server.crt'
client_cert = '../Keys/client.crt'
client_key = '../Keys/client.key'

"""
creation and connection of the secure channel using SSL protocol
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client request details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-rd', '--reader_name', type=str, help='Reader name')
    parser.add_argument('-a', '--authority', type=int, help='Authority number')
    parser.add_argument('-hs', '--handshake', action='store_true', help='Handshake request')
    parser.add_argument('-gk', '--generate_key', action='store_true', help='Generate key request')
    args = parser.parse_args()

    PORT = 5060 + args.authority - 1
    SERVER = config('SERVER_ADDRESS')
    ADDR = (SERVER, PORT)

    sender_name = args.reader_name
    sender_address = config(sender_name + '_ADDRESS')

    gid = sender_name
    reader_address = sender_name

    authority = 'Auth-' + str(args.authority)

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
    conn.connect(ADDR)

    if args.handshake:
        send(authority + " - Start handshake§" + str(process_instance_id) + '§' + reader_address)

    elif args.generate_key:
        signature_sending = sign_number(authority)
        send(
            authority + " - Generate your part of my key§" + gid + '§' + str(process_instance_id) + '§' + reader_address
            + '§' + str(signature_sending))

send(DISCONNECT_MESSAGE)
