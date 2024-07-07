from charm.toolbox.pairinggroup import *
from maabe_class import *
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import block_int
import sqlite3
import json

authorities_names = [
    config('AUTHORITY1_NAME'),
    config('AUTHORITY2_NAME'),
    config('AUTHORITY3_NAME'),
    config('AUTHORITY4_NAME')
]


def retrieve_public_parameters(authority_number, process_instance_id):
    # Connection to SQLite3 authority database
    conn = sqlite3.connect('../databases/authority' + str(authority_number) + '/authority' + str(authority_number) + '.db')
    x = conn.cursor()

    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    public_parameters = result[0][2].encode()
    return public_parameters


def generate_user_key(authority_number, gid, process_instance_id, reader_address):
    # Connection to SQLite3 authority database
    conn = sqlite3.connect('../databases/authority' + str(authority_number) + '/authority' + str(authority_number) + '.db')
    x = conn.cursor()

    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    response = retrieve_public_parameters(authority_number, process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    x.execute("SELECT * FROM private_keys WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    sk1 = result[0][1]
    sk1 = bytesToObject(sk1, groupObj)

    # keygen Bob
    attributes_ipfs_link = block_int.retrieve_users_attributes(process_instance_id)
    getfile = api.cat(attributes_ipfs_link)
    getfile = getfile.replace(b'\\', b'')
    getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
    getfile = getfile.encode('utf-8')
    getfile = getfile.split(b'####')
    attributes_dict = json.loads(getfile[1].decode('utf-8'))
    user_attr1 = attributes_dict[reader_address]
    user_attr1 = [k for k in user_attr1 if k.endswith(authorities_names[int(authority_number) - 1])]
    user_sk1 = maabe.multiple_attributes_keygen(public_parameters, sk1, gid, user_attr1)
    user_sk1_bytes = objectToBytes(user_sk1, groupObj)
    return user_sk1_bytes
