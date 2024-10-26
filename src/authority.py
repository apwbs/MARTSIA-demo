from charm.toolbox.pairinggroup import *
from maabe_class import *
import block_int
import mpc_setup
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import io
import sqlite3
import time
import argparse
from authorities_info import authorities_addresses_and_names_separated


class Authority:
    def __init__(self, authority_number):
        # Initialize Authority instance with private key and database connection
        self.authority_number = authority_number
        self.authority_address = authorities_addresses[authority_number - 1]
        self.__authority_private_key__ = config('AUTHORITY' + str(authority_number) + '_PRIVATEKEY')
        self.__conn__ = sqlite3.connect('../databases/authority' + str(authority_number) + '/authority' + str(authority_number) + '.db')
        self.__x__ = self.__conn__.cursor()

    def save_authorities_names(self, api, process_instance_id):
        # Store name and address of Authority in IPFS and database
        f = io.StringIO()
        for i, addr in enumerate(authorities_addresses):
            f.write('process_instance: ' + str(process_instance_id) + '\n')
            f.write('identification: ' + 'authority ' + str(i + 1) + '\n')
            f.write('name: ' + str(authorities_names[i]) + '\n')
            f.write('address: ' + addr + '\n\n')
        f.seek(0)
        file_to_str = f.read()
        hash_file = api.add_json(file_to_str)
        print(f'ipfs hash: {hash_file}')
        block_int.send_authority_names(self.authority_address, self.__authority_private_key__, process_instance_id, hash_file)
        self.__x__.execute("INSERT OR IGNORE INTO authority_names VALUES (?,?,?)", (str(process_instance_id), hash_file, file_to_str))
        self.__conn__.commit()

    def initial_parameters_hashed(self, groupObj, process_instance_id):
        # Generate hashed initial parameters and save in blockchain and database
        g1_1 = groupObj.random(G1)
        g2_1 = groupObj.random(G2)
        (h1_1, h2_1) = mpc_setup.commit(groupObj, g1_1, g2_1)
        block_int.sendHashedElements(self.authority_address, self.__authority_private_key__, process_instance_id, (h1_1, h2_1))
        self.__x__.execute("INSERT OR IGNORE INTO h_values VALUES (?,?,?)", (str(process_instance_id), h1_1, h2_1))
        self.__conn__.commit()
        g1_1_bytes = groupObj.serialize(g1_1)
        g2_1_bytes = groupObj.serialize(g2_1)
        self.__x__.execute("INSERT OR IGNORE INTO g_values VALUES (?,?,?)", (str(process_instance_id), g1_1_bytes, g2_1_bytes))
        self.__conn__.commit()

    def initial_parameters(self, process_instance_id):
        # Retrieve initial parameters and send to blockchain
        self.__x__.execute("SELECT * FROM g_values WHERE process_instance=?", (str(process_instance_id),))
        result = self.__x__.fetchall()
        g1_1_bytes = result[0][1]
        g2_1_bytes = result[0][2]
        block_int.sendElements(self.authority_address, self.__authority_private_key__, process_instance_id, (g1_1_bytes, g2_1_bytes))

    def generate_public_parameters(self, groupObj, maabe, api, process_instance_id):
        # Generate public parameters from initial hashes and commitments
        hashes1 = []
        hashes2 = []
        com1 = []
        com2 = []
        count = 0
        for auth in authorities_addresses:
            g1g2_hashed = block_int.retrieveHashedElements(authorities_addresses[count], process_instance_id)
            if void_bytes in g1g2_hashed:
                return False
            g1g2 = block_int.retrieveElements(authorities_addresses[count], process_instance_id)
            if void_bytes in g1g2:
                return False
            hashes1.append(g1g2_hashed[0])
            hashes2.append(g1g2_hashed[1])
            com1.append(groupObj.deserialize(g1g2[0]))
            com2.append(groupObj.deserialize(g1g2[1]))
            count += 1
        (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)
        public_parameters = maabe.setup(value1, value2)
        public_parameters_reduced = dict(list(public_parameters.items())[0:3])
        pp_reduced = objectToBytes(public_parameters_reduced, groupObj)
        file_to_str = pp_reduced.decode('utf-8')
        hash_file = api.add_json(file_to_str)
        print(f'ipfs hash: {hash_file}')
        self.__x__.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)", (str(process_instance_id), hash_file, file_to_str))
        self.__conn__.commit()
        block_int.send_parameters_link(self.authority_address, self.__authority_private_key__, process_instance_id, hash_file)
        return True

    def retrieve_public_parameters(self, process_instance_id):
        # Retrieve public parameters from database
        self.__x__.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
        result = self.__x__.fetchall()
        public_parameters = result[0][2].encode()
        return public_parameters

    def generate_pk_sk(self, groupObj, maabe, api, process_instance_id):
        # Generate public and private keys for Authority based on public parameters
        response = self.retrieve_public_parameters(process_instance_id)
        public_parameters = bytesToObject(response, groupObj)
        H = lambda x: group.hash(x, G2)
        F = lambda x: group.hash(x, G2)
        public_parameters["H"] = H
        public_parameters["F"] = F
        (pk1, sk1) = maabe.authsetup(public_parameters, authorities_names[self.authority_number - 1])
        pk1_bytes = objectToBytes(pk1, groupObj)
        sk1_bytes = objectToBytes(sk1, groupObj)
        file_to_str = pk1_bytes.decode('utf-8')
        hash_file = api.add_json(file_to_str)
        print(f'ipfs hash: {hash_file}')
        self.__x__.execute("INSERT OR IGNORE INTO private_keys VALUES (?,?)", (str(process_instance_id), sk1_bytes))
        self.__conn__.commit()
        self.__x__.execute("INSERT OR IGNORE INTO public_keys VALUES (?,?,?)", (str(process_instance_id), hash_file, pk1_bytes))
        self.__conn__.commit()
        block_int.send_publicKey_link(self.authority_address, self.__authority_private_key__, process_instance_id, hash_file)


def main():
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id_env = config('PROCESS_INSTANCE_ID')
    process_instance_id = int(process_instance_id_env)
    parser = argparse.ArgumentParser(description='Authority')
    parser.add_argument('-a', '--authority', type=int, help='Authority number')
    args = parser.parse_args()
    if args.authority < 1 or args.authority > len(authorities_addresses):
        parser.print_help()
    else:
        authority_number = args.authority
        authority = Authority(authority_number)
        print("Phase 0.1")
        authority.save_authorities_names(api, process_instance_id)
        print("Phase 0.2")
        authority.initial_parameters_hashed(groupObj, process_instance_id)
        print("Phase 0.3")
        authority.initial_parameters(process_instance_id)
        print("Phase 0.4")
        while not authority.generate_public_parameters(groupObj, maabe, api, process_instance_id):
            time.sleep(5)
        print("Phase 0.5")
        authority.generate_pk_sk(groupObj, maabe, api, process_instance_id)


if __name__ == '__main__':
    authorities_addresses, authorities_names = authorities_addresses_and_names_separated()
    void_bytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    main()

