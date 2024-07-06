CREATE TABLE authorities_public_keys ( 
    process_instance BIGINT,
    authority_name TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (process_instance, authority_name)
);

CREATE TABLE public_parameters ( 
    process_instance BIGINT,
    ipfs_file_link_hash TEXT,
    public_parameters_values TEXT,
    primary key (process_instance)
);

CREATE TABLE messages (
    process_instance BIGINT,
    message_id TEXT,
    ipfs_file_link_hash TEXT,
    message_file TEXT,
    primary key (process_instance, message_id)
);
