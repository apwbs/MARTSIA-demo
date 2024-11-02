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
from authorities_info import authorities_names_and_addresses

def retrieve_data(authority_address, process_instance_id):
    """Retrieve names, public parameters, and public keys from the specified Authority"""
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    public_key = block_int.retrieve_publicKey_link(authority_address, process_instance_id)
    return authorities, public_parameters, public_key

def generate_pp_pk(process_instance_id):
    """Generate public parameters and public keys for the Authorities"""
    check_authorities = []
    check_parameters = []
    for authority_name, authority_address in authorities_names_and_addresses:
        data = retrieve_data(authority_address, process_instance_id)
        check_authorities.append(data[0])
        check_parameters.append(data[1])
        pk1 = api.cat(data[2])
        pk1 = pk1.decode('utf-8').rstrip('"').lstrip('"').encode('utf-8')
        x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
                  (str(process_instance_id), f"Auth-{authority_name[4:]}", data[2], pk1))
        conn.commit()
    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        getfile = getfile.decode('utf-8').rstrip('"').lstrip('"').encode('utf-8')
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), check_parameters[0], getfile))
        conn.commit()

def retrieve_public_parameters(process_instance_id):
    """Retrieve public parameters for the specified process instance"""
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    if not result:
        return None
    public_parameters = result[0][2]
    return public_parameters

def file_to_base64(file_path):
    """Encode a file to Base64 format"""
    try:
        with open(file_path, 'rb') as file:
            encoded = base64.b64encode(file.read()).decode('utf-8')
        return encoded
    except Exception as e:
        print(f"Error encoding file to Base64: {e}")
        return None

def cipher_data(groupObj, maabe, api, process_instance_id, sender_name, input_files_path, policies_path):
    """Encrypt data using MA-ABE and generate a corresponding IPFS hash"""
    sender_address = config(sender_name + '_ADDRESS')
    sender_private_key = config(sender_name + '_PRIVATEKEY')
    generate_pp_pk(process_instance_id)
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: groupObj.hash(x, G2)
    F = lambda x: groupObj.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    pk = {}
    for authority_name, authority_address in authorities_names_and_addresses:
        x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
                  (str(process_instance_id), f"Auth-{authority_name[4:]}"))
        result = x.fetchall()
        pk1 = result[0][3]
        pk1 = bytesToObject(pk1, groupObj)
        pk[authority_name] = pk1
    
    # Load input files and policies
    input_files_path = os.path.abspath(input_files_path)
    policies_path = os.path.abspath(policies_path)
    with open(policies_path, 'r') as policies_file:
        input_policies = json.load(policies_file)
    
    file_contents = {}
    access_policy = {}
    
    # Convert files to Base64 and prepare access policies
    for file_name, policy in input_policies.items():
        file_path = os.path.join(input_files_path, file_name)
        file_contents[file_name] = file_to_base64(file_path)
        temporal = "".join(f"{process_instance_id_env}@{authority_name} and " for authority_name, _ in authorities_names_and_addresses)
        access_policy[file_name] = f"({temporal[:-5]}) and {policy}"
    
    keys = []
    header = []
    
    # Clear cache file
    with open('../src/.cache', 'w') as file:
        pass
    
    # Encrypt files and generate headers
    for index, (file_name, policy) in enumerate(input_policies.items()):
        key_group = groupObj.random(GT)
        key_encrypt = groupObj.serialize(key_group)
        keys.append(key_encrypt)
        key_encrypt_deser = groupObj.deserialize(key_encrypt)
        ciphered_key = maabe.encrypt(public_parameters, pk, key_encrypt_deser, access_policy[file_name])
        ciphered_key_bytes = objectToBytes(ciphered_key, groupObj)
        ciphered_key_bytes_string = ciphered_key_bytes.decode('utf-8')
        
        # Encrypt file contents and prepare headers
        cipher = cryptocode.encrypt(file_contents[file_name], str(keys[index]))
        dict_pol = {
            'CipheredKey': ciphered_key_bytes_string,
            'FileName': file_name,
            'EncryptedFile': cipher
        }
        
        # Handle multiple policies with slice ID
        if len(access_policy) > 1:
            now = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))
            random.seed(now)
            slice_id = random.randint(10_000_000_000_000_000_000, 18_446_744_073_709_551_615)
            dict_pol['Slice_id'] = slice_id
            print(f'slice id {file_name}: {slice_id}')
            with open('../src/.cache', 'a') as file:
                file.write(f'slice id {file_name}: {slice_id} | slice{index + 1}\n')
        
        header.append(dict_pol)
    
    # Generate metadata and send to IPFS
    now = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    message_id = random.randint(10_000_000_000_000_000_000, 18_446_744_073_709_551_615)
    metadata = {
        'sender': sender_address,
        'process_instance_id': int(process_instance_id),
        'message_id': message_id
    }
    print(f'message id: {message_id}')
    with open('../src/.cache', 'a') as file:
        file.write(f'message id: {message_id} | last_message_id\n')
    
    json_total = {'metadata': metadata, 'header': header}
    hash_file = api.add_json(json_total)
    print(f'ipfs hash: {hash_file}')
    with open('../src/.cache', 'a') as file:
        file.write(f'ipfs hash: {hash_file}\n')
    
    x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
              (str(process_instance_id), str(message_id), hash_file, str(json_total)))
    conn.commit()
    
    # Send the message link to IPFS
    block_int.send_MessageIPFSLink(sender_address, sender_private_key, message_id, hash_file)

if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id_env = config('PROCESS_INSTANCE_ID')
    process_instance_id = int(process_instance_id_env)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sender_name', type=str, help='Sender address of the requester')
    parser.add_argument('-i', '--input', type=str, help='Path to the input-file to load.')
    parser.add_argument('-p', '--policies', type=str, help='Path to the policies-file to load.')
    args = parser.parse_args()
    
    # Connection to SQLite3 data_owner database
    conn = sqlite3.connect('../databases/data_owner/data_owner.db')
    x = conn.cursor()
    authorities_names_and_addresses = authorities_names_and_addresses()
    cipher_data(groupObj, maabe, api, process_instance_id, args.sender_name, args.input, args.policies)

