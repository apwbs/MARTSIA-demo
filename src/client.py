import socket
import ssl
from decouple import config
from hashlib import sha512
import sqlite3
import argparse
import sys
import io


def sign_number(authority_invoked):
    # Retrieve the handshake number for the specified Authority and Reader address
    x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND authority_name=? AND reader_address=?",
              (str(process_instance_id), authority_invoked, reader_address))
    result = x.fetchall()
    number_to_sign = result[0][3]

    # Retrieve the RSA private key for the reader Address
    x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = x.fetchall()
    private_key = result[0]
    private_key_n = int(private_key[1])
    private_key_d = int(private_key[2])

    # Hash the number to sign and create a digital signature
    msg = bytes(str(number_to_sign), 'utf-8')
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, private_key_d, private_key_n)
    return signature


def receive_message():
    # Function to handle receiving messages
    message = ""
    while True:
        data = conn.recv(1024).decode(FORMAT)
        if not data:
            break
        message += data

        # Check for specific message types and return them
        if message.startswith("Number to sign:"):
            return message
        elif message.startswith("Here is my partial key:"):
            return message


def send(msg):
    # Function to send a message and handle the response
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (int(HEADER) - len(send_length))
    conn.send(send_length)
    conn.send(message)
    receive = receive_message()
    if len(receive) != 0:
        if receive.startswith('Number to sign:'):
            # Insert handshake number into the database
            x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?,?)",
                      (str(process_instance_id), reader_address, authority, receive[16:]))
            connection.commit()
            return True
        # Insert generated description keys into the database
        x.execute("INSERT OR IGNORE INTO authorities_generated_decription_keys VALUES (?,?,?,?)",
                  (str(process_instance_id), reader_address, authority, receive[23:]))
        connection.commit()


if __name__ == '__main__':
    # Set up UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Connection to SQLite3 Reader database
    connection = sqlite3.connect('../databases/reader/reader.db')
    x = connection.cursor()

    # Load environment variables and configurations
    process_instance_id_env = config('PROCESS_INSTANCE_ID')
    process_instance_id = int(process_instance_id_env)
    HEADER = config('HEADER')
    FORMAT = 'utf-8'
    server_sni_hostname = config('SERVER_SNI_HOSTNAME')
    DISCONNECT_MESSAGE = "!DISCONNECT"
    server_cert = '../Keys/server.crt'
    client_cert = '../Keys/client.crt'
    client_key = '../Keys/client.key'

    # Set up argument parser for command-line inputs
    parser = argparse.ArgumentParser(description="Client request details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-rd', '--requester_name', type=str, help='Requester name')
    parser.add_argument('-a', '--authority', type=int, help='Authority number')
    parser.add_argument('-hs', '--handshake', action='store_true', help='Handshake request')
    parser.add_argument('-gk', '--generate_key', action='store_true', help='Generate key request')
    args = parser.parse_args()

    # Determine Authority address and port
    PORT = 5060 + args.authority - 1
    SERVER = config('SERVER_ADDRESS')
    ADDR = (SERVER, PORT)

    # Retrieve sender and reader addresses
    sender_address = config(args.requester_name + '_ADDRESS')
    gid = sender_address
    reader_address = sender_address
    authority = 'Auth-' + str(args.authority)

    # Check if a key is already present for the given Authority
    x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=? AND reader_address=?",
                  (str(process_instance_id), authority, reader_address))
    result = x.fetchall()
    if result:
        if args.generate_key:
            print(f"✅ Key already present for {authority}!")
        exit()

    # Create SSL context for secure connection
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    # Create a socket and wrap it with SSL
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
    conn.connect(ADDR)

    # Handle handshake and key generation requests
    if args.handshake:
        send(authority + " - Start handshake§" + str(process_instance_id) + '§' + reader_address)
        print(f"✅ Handshake completed for {authority} and requester {args.requester_name}!")
    elif args.generate_key:
        signature_sending = sign_number(authority)
        send(
            authority + " - Generate your part of my key§" + gid + '§' + str(process_instance_id) + '§' + reader_address
            + '§' + str(signature_sending))
        print(f"✅ Key generation completed for {authority} and requester {args.requester_name}!")

