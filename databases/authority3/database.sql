CREATE TABLE authority_names ( 
    process_instance TEXT,
    ipfs_file_link_hash TEXT,
    authority_names_file TEXT,
    primary key (process_instance)
);

CREATE TABLE public_keys ( 
    process_instance TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (process_instance)
);

CREATE TABLE private_keys ( 
    process_instance TEXT,
    private_key TEXT,
    primary key (process_instance)
);

CREATE TABLE public_parameters ( 
    process_instance TEXT,
    ipfs_file_link_hash TEXT,
    public_parameters_values TEXT,
    primary key (process_instance)
);

CREATE TABLE g_values ( 
    process_instance TEXT,
    g_1 TEXT,
    g_2 TEXT,
    primary key (process_instance)
);

CREATE TABLE h_values ( 
    process_instance TEXT,
    h_1 TEXT,
    h_2 TEXT,
    primary key (process_instance)
);

CREATE TABLE handshake_numbers ( 
    process_instance TEXT,
    reader_address TEXT,
    handshake_number TEXT,
    primary key (process_instance, reader_address)
);

CREATE TABLE readers_public_keys ( 
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (reader_address)
);
