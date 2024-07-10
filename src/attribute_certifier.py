import json
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient
import argparse

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

attribute_certifier_address = config('CERTIFIER_ADDRESS')
private_key = config('CERTIFIER_PRIVATEKEY')

# Connection to SQLite3 attribute_certifier database
conn = sqlite3.connect('../databases/attribute_certifier/attribute_certifier.db')
x = conn.cursor()

def store_process_id_to_env(value):
    name = 'PROCESS_INSTANCE_ID'
    with open('../src/.env', 'r', encoding='utf-8') as file:
        data = file.readlines()
    for line in data:
        if line.startswith(name):
            data.remove(line)
            break
    line = "\n" + name + "=" + value + "\n"
    data.append(line)

    with open('../src/.env', 'w', encoding='utf-8') as file:
        file.writelines(data)

def retrieve_authorities():
    authorities = []
    count = 1
    
    while True:
        name_key = f'AUTHORITY{count}_NAME'
        name = config(name_key, default=None)
        if not name:
            break
        authorities.append(name)
        count += 1
    
    return authorities

def generate_attributes(roles_file):
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(1, 2 ** 64)
    print(f'process instance id: {process_instance_id}')

    with open(roles_file, 'r') as file:
        roles_data = json.load(file)

    roles = {key: [value] if not isinstance(value, list) else value for key, value in roles_data.items()}

    authorities = retrieve_authorities()

    dict_users = {}
    for role, attributes in roles.items():
        address = config(f'{role}_ADDRESS')
        dict_users[address] = [f'{process_instance_id}@{auth}' for auth in authorities] + attributes

    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)

    file_to_str = f.read()

    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    block_int.send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file)

    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()

    store_process_id_to_env(str(process_instance_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Certifier configuration')
    parser.add_argument('-i', '--input', type=str, help='Specify the path of the roles.json file')
    args = parser.parse_args()
    if args.input:
        generate_attributes(args.input)
    else:
        parser.print_help()

