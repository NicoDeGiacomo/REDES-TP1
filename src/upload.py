import argparse
import logging
import os
import errno
#import protocol.udp_client as udp_client
import protocol
from action import Action


logger = logging.getLogger(__name__)


def upload(host: str, port: int, path: str, file_name: str):
    logger.info(f"""Starting client uploading file {file_name} at location {path} 
        to server {host}:{port}.""")
    if not os.path.exists(path):
        logger.error(f"Directory does not exist: {path}")
        return errno.ENOENT

    file_name_length = len(file_name)

    if file_name_length > 63:
        logger.error(f"Filename length is {file_name_length}. Must be 1-63 characters long.")
        return errno.EINVAL
    
    file_path = os.path.join(path, file_name)
    if not os.path.isfile(file_path):
        logger.error(f"File not found at path: {file_path}")
        return errno.ENOENT
    
    logger.info(f"File {file_name} found, proceeding with upload.")
    client_protocol = protocol.StopAndWait("10.0.0.2", (host, port), os.path.join(path, file_name))
    logger.info(f"Stablishing connection with server")
    client_protocol.stablish_connection(Action.UPLOAD.value)
    logger.info(f"Starting file uploading")
    client_protocol.start_upload()

    


    """upload_bit = 1
    #S&W
    protocol_bit = 1
    file_name_bytes = file_name.encode() # utf-8 by default
    first_byte = (upload_bit << 7) | (protocol_bit << 6) | file_name_length
    header = bytearray()
    header.append(first_byte)
    header.extend(file_name_bytes)
    logger.info(f"Handshake header created\n")"""
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts a client that uploads a file to a server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="decrease output verbosity")
    parser.add_argument('-H', '--host', action='store', default="10.0.0.1",
                        help="server IP address")
    parser.add_argument('-p', '--port', action='store', default=12345,
                        help="server port")
    parser.add_argument('-s', '--src', action='store', default="files/client_storage",
                        help="source file path")
    parser.add_argument('-n', '--name', action='store', default="velociraptor.jpg",
                        help="file name")

    args = parser.parse_args()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    upload(args.host, args.port, args.src, args.name)
