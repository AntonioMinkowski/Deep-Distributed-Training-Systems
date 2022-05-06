from FTP_Server.FTP import *
import pickle

# Initialize main server variables
BUFFER              = 4096
FORMAT              = 'utf-8'
DISCONNECT_MESSAGE  = '!DISCONNECT'

# Create the client handler function
def client_handler_train(conn, addr, model_path, config_path, dataset_status, dataset, status, Batch=None):
    print(f'[NEW CONNECTION] {addr} connected.')

    # Sending status and receiving response
    conn.sendall(status.encode(FORMAT))
    response = conn.recv(30).decode(FORMAT)
    print(response)

    # Start sending model and config files
    FTP_Sender(conn, model_path)
    FTP_Sender(conn, config_path)

    # Wait for "getdataset_status" command
    cmd = conn.recv(32).decode(FORMAT)

    # Send the dataset status
    if cmd == 'getdataset_status':
        conn.sendall(str(dataset_status).encode(FORMAT))

    # Waiting for "getdataset" command to send the dataset
    cmd = conn.recv(32).decode(FORMAT)
    if cmd == 'getdataset':
    
        if dataset_status == 1:
            # Send the X (input) data
            FTP_Sender(conn, 'Input_data.npz', pickle.dumps(dataset[0])) 

            # Send the Y (output) data
            FTP_Sender(conn, 'Output_data.npz', pickle.dumps(dataset[1]))

        elif dataset_status == 2:
            conn.sendall(dataset) 

        else:
            # Sending Batch size to the client and receive a done response
            conn.sendall(pickle.dumps(Batch))

            response = conn.recv(32).decode(FORMAT)
            print(response)

            # Sending dataset's name to the client and receive a done response
            conn.sendall(dataset.encode(FORMAT))

            response = conn.recv(32).decode(FORMAT)
            print(response)

    # Waiting for DISCONNECT command
    cmd = conn.recv(32).decode(FORMAT)
    if cmd == DISCONNECT_MESSAGE:
        conn.close()