from charm.toolbox.pairinggroup import *
from maabe_class import *
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import block_int
import sqlite3
import json
from authorities_info import authorities_names

def retrieve_public_parameters(authority_number, process_instance_id):
    # Connect to the SQLite3 Authority database for the specified Authority
    conn = sqlite3.connect('../databases/authority' + str(authority_number) + '/authority' + str(authority_number) + '.db')
    x = conn.cursor()
    
    # Query the public parameters based on the process instance ID
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    
    # Get the public parameters and encode them for use
    public_parameters = result[0][2].encode()
    return public_parameters

def generate_user_key(authority_number, gid, process_instance_id, reader_address):
    # Get the names of the Authorities for attribute retrieval
    authorities_names_value = authorities_names()
    
    # Connect to the SQLite3 Authority database
    conn = sqlite3.connect('../databases/authority' + str(authority_number) + '/authority' + str(authority_number) + '.db')
    x = conn.cursor()
    
    # Initialize the pairing group and MA-ABE instance
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    
    # Connect to the IPFS API
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    
    # Retrieve public parameters for the given Authority and process instance
    response = retrieve_public_parameters(authority_number, process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    
    # Define hash functions H and F for the public parameters
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    
    # Retrieve the user's private key based on the process instance ID
    x.execute("SELECT * FROM private_keys WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    sk1 = result[0][1]
    sk1 = bytesToObject(sk1, groupObj)
    
    # Retrieve user attributes stored in IPFS for the given process instance
    attributes_ipfs_link = block_int.retrieve_users_attributes(process_instance_id)
    getfile = api.cat(attributes_ipfs_link)
    
    # Clean up the retrieved file data and decode it
    getfile = getfile.replace(b'\\', b'')
    getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
    getfile = getfile.encode('utf-8')
    getfile = getfile.split(b'####')
    
    # Load the user attributes into a dictionary
    attributes_dict = json.loads(getfile[1].decode('utf-8'))
    user_attr1 = attributes_dict[reader_address]
    
    # Filter user attributes based on the Authority name
    user_attr1 = [k for k in user_attr1 if k.endswith(authorities_names_value[int(authority_number) - 1])]
    
    # Generate the user's secret key using attributes
    user_sk1 = maabe.multiple_attributes_keygen(public_parameters, sk1, gid, user_attr1)
    
    # Convert the user secret key to bytes for transmission
    user_sk1_bytes = objectToBytes(user_sk1, groupObj)
    return user_sk1_bytes

