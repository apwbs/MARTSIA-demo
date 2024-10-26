from charm.toolbox.pairinggroup import *
from charm.core.engine.util import bytesToObject
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
from authorities_info import authorities_addresses_and_names_separated


def merge_dicts(*dict_args):
    """
    Merge dictionaries, with precedence given to latter dictionaries
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def retrieve_data(authority_address, process_instance_id):
    """
    Retrieve Authorities and public parameters for the given process instance
    """
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    return authorities, public_parameters


def generate_public_parameters(process_instance_id):
    """
    Generate and store public parameters if consistent across Authorities
    """
    check_authorities = []
    check_parameters = []
    for authority_address in authorities_addresses:
        data = retrieve_data(authority_address, process_instance_id)
        check_authorities.append(data[0])
        check_parameters.append(data[1])
    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), check_parameters[0], getfile))
        conn.commit()


def base64_to_file(encoded_data, output_file_path):
    """
    Decode a Base64 encoded string and save it as a file
    """
    try:
        decoded_data = base64.b64decode(encoded_data.encode('utf-8'))
        with open(output_file_path, 'wb') as file:
            file.write(decoded_data)
    except Exception as e:
        print(f"Error decoding Base64 to file: {e}")


def retrieve_public_parameters(process_instance_id):
    """
    Retrieve public parameters for the process instance
    """
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
    """
    Perform decryption using public parameters and user secret key
    """
    test = remaining['CipheredKey'].encode('utf-8')
    ct = bytesToObject(test, groupObj)
    v2 = maabe.decrypt(public_parameters, user_sk, ct)
    v2 = groupObj.serialize(v2)
    output_folder_path = os.path.abspath(output_folder)
    decryptedFile = cryptocode.decrypt(remaining['EncryptedFile'], str(v2))
    base64_to_file(decryptedFile, output_folder_path+"/"+remaining['FileName'])


def start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged):
    """
    Main decryption workflow based on the provided message and slice IDs
    """
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    for authority_name in authorities_names:
        f = authority_name[0].upper() + authority_name[1:].lower()
        prefix = ''.join(filter(str.isalpha, f))
        number = ''.join(filter(str.isdigit, f))
        transformed_string = f"{prefix}-{number}"
        x.execute("SELECT * FROM authorities_generated_decription_keys WHERE process_instance=? AND authority_name=? AND reader_address=?",
                  (str(process_instance_id), transformed_string, sender_address))
        result = x.fetchall()
        user_sk1 = result[0][3]
        user_sk1 = user_sk1.encode()
        user_sk1 = bytesToObject(user_sk1, groupObj)
        merged = merge_dicts(merged, user_sk1)
    user_sk = {'GID': sender_address, 'keys': merged}
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
    authorities_addresses, authorities_names = authorities_addresses_and_names_separated()
    process_instance_id_env = config('PROCESS_INSTANCE_ID')
    # Connection to SQLite3 data_owner database
    conn = sqlite3.connect('../databases/reader/reader.db')
    x = conn.cursor()
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)
    parser = argparse.ArgumentParser(description="Reader details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--message_id", type=int, help="message id")
    parser.add_argument("-s", "--slice_id", type=int, help="slice id")
    parser.add_argument("--reader_name", type=str, help="Name of the requester")
    parser.add_argument("-o", "--output_folder", type=str, help="Path to the output folder")
    args = parser.parse_args()
    message_id = args.message_id
    slice_id = args.slice_id
    sender_address = config(args.reader_name + '_ADDRESS')
    output_folder = args.output_folder
    merged = {}
    start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged)

