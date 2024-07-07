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


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (int(HEADER) - len(send_length))
    conn.send(send_length)
    # print(send_length)
    conn.send(message)
    receive = conn.recv(6000).decode(FORMAT)
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


manufacturer = config('MANUFACTURER_ADDRESS')
electronics = config('SUPPLIER1_ADDRESS')
mechanics = config('SUPPLIER2_ADDRESS')
process_instance_id_env = config('PROCESS_INSTANCE_ID')

reader_address = manufacturer
process_instance_id = int(process_instance_id_env)
gid = "bob"

parser =argparse.ArgumentParser(description="Client request details", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument('-m', '--message_id', type=str, default=message_id, help='Message ID')
#parser.add_argument('-s', '--slice_id', type=str, default=slice_id, help='Slice ID')
parser.add_argument('-g', '--gid', type=str, default=gid, help='Slice ID')
parser.add_argument('-rd', '--reader_address', type=str, default=reader_address, help='Reader address')
parser.add_argument('-a', '--authority', type=int, default=1, help='Authority')
parser.add_argument('-hs', '--handshake', action='store_true', help='Handshake')
parser.add_argument('-gk', '--generate_key', action='store_true', help='Generate key')
#parser.add_argument('-ad','--access_data',  action='store_true', help='Access data')
args = parser.parse_args()

#message_id = args.message_id
#slice_id = args.slice_id
gid = args.gid
reader_address = args.reader_address

authority = 'Auth-' + str(args.authority)

HEADER = config('HEADER')
PORT = 5060 + args.authority - 1
FORMAT = 'utf-8'
server_sni_hostname = config('SERVER_SNI_HOSTNAME')
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = config('SERVER_ADDRESS')
ADDR = (SERVER, PORT)
server_cert = '../Keys/server.crt'
client_cert = '../Keys/client.crt'
client_key = '../Keys/client.key'

"""
creation and connection of the secure channel using SSL protocol
"""

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect(ADDR)

if args.handshake:
    send(authority + " - Start handshake§" + str(process_instance_id) + '§' + reader_address)

elif args.generate_key:
    signature_sending = sign_number(authority)
    send(authority + " - Generate your part of my key§" + gid + '§' + str(process_instance_id) + '§' + reader_address
        + '§' + str(signature_sending))

# exit()
# input()

send(DISCONNECT_MESSAGE)
