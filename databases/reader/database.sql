CREATE TABLE authorities_public_keys ( 
    process_instance TEXT,
    authority_name TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (process_instance, authority_name)
);

CREATE TABLE public_parameters ( 
    process_instance TEXT,
    ipfs_file_link_hash TEXT,
    public_parameters_values TEXT,
    primary key (process_instance)
);

CREATE TABLE rsa_public_key (
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    publicKey_n TEXT,
    publicKey_e TEXT,
    primary key (reader_address)
);

CREATE TABLE rsa_private_key (
    reader_address TEXT,
    privateKey_n TEXT,
    privateKey_d TEXT,
    primary key (reader_address)
);

CREATE TABLE handshake_number ( 
    process_instance TEXT,
    reader_address TEXT,
    authority_name TEXT,
    number_to_sign TEXT,
    primary key (process_instance, reader_address, authority_name)
);

CREATE TABLE authorities_generated_decription_keys ( 
    process_instance TEXT,
    reader_address TEXT,
    authority_name TEXT,
    decription_key TEXT,
    primary key (process_instance, reader_address, authority_name)
);
