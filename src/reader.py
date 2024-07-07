from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
import block_int
import ipfshttpclient
import json
import os
import base64
from maabe_class import *
from decouple import config
import sqlite3
import argparse

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

process_instance_id_env = config('PROCESS_INSTANCE_ID')

# Connection to SQLite3 data_owner database
conn = sqlite3.connect('../databases/reader/reader.db')
x = conn.cursor()


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def retrieve_data(authority_address, process_instance_id):
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    return authorities, public_parameters


def generate_public_parameters(process_instance_id):
    check_authorities = []
    check_parameters = []

    data = retrieve_data(authority1_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority2_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority3_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority4_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), check_parameters[0], getfile))
        conn.commit()


def base64_to_file(encoded_data, output_file_path):
    try:
        decoded_data = base64.b64decode(encoded_data.encode('utf-8'))
        with open(output_file_path, 'wb') as file:
            file.write(decoded_data)
    except Exception as e:
        print(f"Error decoding Base64 to file: {e}")


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    try:
        public_parameters = result[0][2]
    except IndexError:
        generate_public_parameters(process_instance_id)
        x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
        result = x.fetchall()
        public_parameters = result[0][2]
    return public_parameters


def actual_decryption(remaining, public_parameters, user_sk, output_folder):
    test = remaining['CipheredKey'].encode('utf-8')

    ct = bytesToObject(test, groupObj)
    v2 = maabe.decrypt(public_parameters, user_sk, ct)
    v2 = groupObj.serialize(v2)

    output_folder_path = os.path.abspath(output_folder)
    decryptedFile = cryptocode.decrypt(remaining['EncryptedFile'], str(v2))
    base64_to_file(decryptedFile, output_folder_path+"/"+remaining['FileName'])


def start(process_instance_id, message_id, slice_id, gid, output_folder):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # keygen Bob
    # we can do this with a for loop
    x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-1'))
    result = x.fetchall()
    user_sk1 = result[0][2]
    user_sk1 = user_sk1.encode()
    user_sk1 = bytesToObject(user_sk1, groupObj)

    x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-2'))
    result = x.fetchall()
    user_sk2 = result[0][2]
    user_sk2 = user_sk2.encode()
    user_sk2 = bytesToObject(user_sk2, groupObj)

    x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-3'))
    result = x.fetchall()
    user_sk3 = result[0][2]
    user_sk3 = user_sk3.encode()
    user_sk3 = bytesToObject(user_sk3, groupObj)

    x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-4'))
    result = x.fetchall()
    user_sk4 = result[0][2]
    user_sk4 = user_sk4.encode()
    user_sk4 = bytesToObject(user_sk4, groupObj)

    user_sk = {'GID': gid, 'keys': merge_dicts(user_sk1, user_sk2, user_sk3, user_sk4)}

    # decrypt
    response = block_int.retrieve_MessageIPFSLink(message_id)
    ciphertext_link = response[0]
    getfile = api.cat(ciphertext_link)
    ciphertext_dict = json.loads(getfile)
    sender = response[1]
    if ciphertext_dict['metadata']['process_instance_id'] == int(process_instance_id) \
            and ciphertext_dict['metadata']['message_id'] == int(message_id) \
            and ciphertext_dict['metadata']['sender'] == sender:
        slice_check = ciphertext_dict['header']
        if len(slice_check) == 1:
            actual_decryption(ciphertext_dict['header'][0], public_parameters, user_sk, output_folder)
        elif len(slice_check) > 1:
            for remaining in slice_check:
                if remaining['Slice_id'] == slice_id:
                    actual_decryption(remaining, public_parameters, user_sk, output_folder)


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    process_instance_id = int(process_instance_id_env)
    parser = argparse.ArgumentParser(description="Reader details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--message_id", type=int, help="message id", default=0)
    parser.add_argument("-s", "--slice_id", type=int, help="slice id", default=0)
    parser.add_argument("-g", "--generate", action="store_true", help='Retrieval')
    parser.add_argument("--gid", type=str, help="gid", default="bob")
    parser.add_argument("-o", "--output_folder", type=str, help="Path to the output folder")
    args = parser.parse_args()
    if args.generate:
        generate_public_parameters(process_instance_id)
    else:
        message_id = args.message_id
        slice_id = args.slice_id
        gid = args.gid
        output_folder = args.output_folder
        start(process_instance_id, message_id, slice_id, gid, output_folder)
