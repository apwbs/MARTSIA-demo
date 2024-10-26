from decouple import config
from Crypto.PublicKey import RSA
import ipfshttpclient
import block_int
import sqlite3
import io
import argparse


def generate_keys(reader_name):
    # Connect to the reader's SQLite3 database
    conn = sqlite3.connect('../databases/reader/reader.db')
    x = conn.cursor()
    
    # Retrieve reader's address and private key from environment variables
    reader_address = config(reader_name + '_ADDRESS')
    private_key = config(reader_name + '_PRIVATEKEY')
    
    # Check if an RSA key already exists for the reader's address
    x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = x.fetchall()
    if result:
        print("rsa key already present")
        exit()
    
    # Generate a new RSA key pair
    keyPair = RSA.generate(bits=1024)
    f = io.StringIO()
    f.write('reader_address: ' + reader_address + '###')
    f.write(str(keyPair.n) + '###' + str(keyPair.e))
    f.seek(0)
    
    # Upload the public key to IPFS and get the hash
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')
    
    # Store the public key hash on the blockchain
    block_int.send_publicKey_readers(reader_address, private_key, hash_file)
    
    # Save the private and public keys in the reader's database
    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)", (reader_address, str(keyPair.n), str(keyPair.d)))
    conn.commit()
    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
              (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
    conn.commit()


if __name__ == "__main__":
    # Parse command-line arguments for specifying the reader name
    parser = argparse.ArgumentParser(description='Reader name', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', '--reader', type=str, help='Specify a reader name')
    args = parser.parse_args()
    
    # Generate keys if the reader name argument is provided
    if args.reader:
        generate_keys(args.reader)
    else:
        parser.print_help()

