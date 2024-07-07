import os

from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
import block_int
from decouple import config
import ipfshttpclient
import json
from maabe_class import *
from datetime import datetime
import random
import base64
import sqlite3
import argparse

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

process_instance_id_env = config('PROCESS_INSTANCE_ID')

# Connection to SQLite3 data_owner database
conn = sqlite3.connect('../databases/data_owner/data_owner.db')
x = conn.cursor()


def retrieve_data(authority_address, process_instance_id):
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    public_key = block_int.retrieve_publicKey_link(authority_address, process_instance_id)
    return authorities, public_parameters, public_key


def generate_pp_pk(process_instance_id):
    check_authorities = []
    check_parameters = []

    data = retrieve_data(authority1_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk1 = api.cat(data[2])
    pk1 = pk1.decode('utf-8').rstrip('"').lstrip('"')
    pk1 = pk1.encode('utf-8')

    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-1', data[2], pk1))
    conn.commit()

    data = retrieve_data(authority2_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk2 = api.cat(data[2])
    pk2 = pk2.decode('utf-8').rstrip('"').lstrip('"')
    pk2 = pk2.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-2', data[2], pk2))
    conn.commit()

    data = retrieve_data(authority3_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk3 = api.cat(data[2])
    pk3 = pk3.decode('utf-8').rstrip('"').lstrip('"')
    pk3 = pk3.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-3', data[2], pk3))
    conn.commit()

    data = retrieve_data(authority4_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk4 = api.cat(data[2])
    pk4 = pk4.decode('utf-8').rstrip('"').lstrip('"')
    pk4 = pk4.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-4', data[2], pk4))
    conn.commit()

    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
        getfile = getfile.encode('utf-8')
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), check_parameters[0], getfile))
        conn.commit()


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    if not result:
        return None
    public_parameters = result[0][2]
    return public_parameters


def file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            encoded = base64.b64encode(file.read()).decode('utf-8')
        return encoded
    except Exception as e:
        print(f"Error encoding file to Base64: {e}")
        return None


def cipher_data(groupObj, maabe, api, process_instance_id, sender_name, input_files_path, policies_path):
    sender_address = config(sender_name + '_ADDRESS')
    sender_private_key = config(sender_name + '_PRIVATEKEY')

    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-1'))
    result = x.fetchall()
    pk1 = result[0][3]
    pk1 = bytesToObject(pk1, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-2'))
    result = x.fetchall()
    pk2 = result[0][3]
    pk2 = bytesToObject(pk2, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-3'))
    result = x.fetchall()
    pk3 = result[0][3]
    pk3 = bytesToObject(pk3, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-4'))
    result = x.fetchall()
    pk4 = result[0][3]
    pk4 = bytesToObject(pk4, groupObj)

    pk = {config('AUTHORITY1_NAME'): pk1, config('AUTHORITY2_NAME'): pk2, config('AUTHORITY3_NAME'): pk3,
          config('AUTHORITY4_NAME'): pk4}

    input_files_path = os.path.abspath(input_files_path)
    policies_path = os.path.abspath(policies_path)

    with open(policies_path, 'r') as policies_file:
        input_policies = json.load(policies_file)

    file_contents = {}
    access_policy = {}

    for file_name, policy in input_policies.items():
        file_path = os.path.join(input_files_path, file_name)
        file_contents[file_name] = file_to_base64(file_path)

        auth1 = config('AUTHORITY1_NAME')
        auth2 = config('AUTHORITY2_NAME')
        auth3 = config('AUTHORITY3_NAME')
        auth4 = config('AUTHORITY4_NAME')
        access_policy[file_name] = (
            f'({str(process_instance_id_env)}@{auth1} and {str(process_instance_id_env)}@{auth2} and '
            f'{str(process_instance_id_env)}@{auth3} and {str(process_instance_id_env)}@{auth4}) and {policy}'
        )

    keys = []
    header = []
    for index, (file_name, policy) in enumerate(input_policies.items()):
        key_group = groupObj.random(GT)
        key_encrypt = groupObj.serialize(key_group)
        keys.append(key_encrypt)
        key_encrypt_deser = groupObj.deserialize(key_encrypt)

        ciphered_key = maabe.encrypt(public_parameters, pk, key_encrypt_deser, access_policy[file_name])
        ciphered_key_bytes = objectToBytes(ciphered_key, groupObj)
        ciphered_key_bytes_string = ciphered_key_bytes.decode('utf-8')

        if len(access_policy) == 1:
            cipher = cryptocode.encrypt(file_contents[file_name], str(keys[index]))
            dict_pol = {'CipheredKey': ciphered_key_bytes_string, "FileName": file_name, "EncryptedFile": cipher}
            header.append(dict_pol)
        else:
            now = datetime.now()
            now = int(now.strftime("%Y%m%d%H%M%S%f"))
            random.seed(now)
            slice_id = random.randint(1, 2 ** 64)
            cipher = cryptocode.encrypt(file_contents[file_name], str(keys[index]))
            dict_pol = {'Slice_id': slice_id, 'CipheredKey': ciphered_key_bytes_string, 'FileName': file_name,
                        "EncryptedFile": cipher}
            print(f'slice id {file_name}: {slice_id}')
            header.append(dict_pol)

    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    message_id = random.randint(1, 2 ** 64)
    metadata = {'sender': sender_address, 'process_instance_id': int(process_instance_id),
                'message_id': message_id}
    print(f'message id: {message_id}')

    json_total = {'metadata': metadata, 'header': header}

    # encoded = cryptocode.encrypt("Ciao Marzia!", str(key_encrypt1))

    hash_file = api.add_json(json_total)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
              (str(process_instance_id), str(message_id), hash_file, str(json_total)))
    conn.commit()

    block_int.send_MessageIPFSLink(sender_address, sender_private_key, message_id, hash_file)


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', action='store_true')
    parser.add_argument('-c', '--cipher', action='store_true')
    parser.add_argument('-s', '--sender_name', type=str, help='Sender address of the requester')
    parser.add_argument('-i', '--input', type=str, help='Path to the input-file to load.')
    parser.add_argument('-p', '--policies', type=str, help='Path to the policies-file to load.')

    args = parser.parse_args()
    if args.generate:
        if not retrieve_public_parameters(process_instance_id):
            generate_pp_pk(process_instance_id)
    elif args.cipher:
        cipher_data(groupObj, maabe, api, process_instance_id, args.sender_name, args.input, args.policies)
    else:
        parser.print_help()
