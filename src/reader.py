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

# Function to dynamically retrieve authorities addresses and names
def retrieve_authorities():
    authorities_list = []
    authorities_names = []
    count = 1
    # Loop to retrieve all authority addresses and names until no more are found
    while True:
        address_key = f'AUTHORITY{count}_ADDRESS'
        name_key = f'AUTHORITY{count}_NAME'
        
        # Check if the config key exists, if not, break the loop
        if not config(address_key, default=None) or not config(name_key, default=None):
            break
        # Append address and name to respective lists
        authorities_list.append(config(address_key))
        authorities_names.append(config(name_key))
        count += 1
    return authorities_list, authorities_names
    
authorities_list, authorities_names = retrieve_authorities()

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
    for e in authorities_list:
        data = retrieve_data(e, process_instance_id)
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

def start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    for e in authorities_names:
        f = e[0].upper() + e[1:].lower()
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
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)
    parser = argparse.ArgumentParser(description="Reader details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--message_id", type=int, help="message id")
    parser.add_argument("-s", "--slice_id", type=int, help="slice id")
    parser.add_argument("-g", "--generate_parameters", action="store_true", help='Retrieval of public parameters')
    parser.add_argument("-a", "--access", action="store_true", help='Access data')
    parser.add_argument("--reader_name", type=str, help="Name of the requester")
    parser.add_argument("-o", "--output_folder", type=str, help="Path to the output folder")
    args = parser.parse_args()
    if args.generate_parameters:
        generate_public_parameters(process_instance_id)
    elif args.access:
        message_id = args.message_id
        slice_id = args.slice_id
        sender_address = config(args.reader_name + '_ADDRESS')
        output_folder = args.output_folder
        merged={}
        start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged)
