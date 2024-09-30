import argparse
import logging
import os
import errno
import stop_and_wait
from action import Action
from tcp_sack_sender import TCPSAckSender

logger = logging.getLogger(__name__)


def upload(host: str, port: int, path: str, file_name: str, protocol: int) -> int:
    logger.info(f"""Starting client uploading file {file_name} at location {path} 
        to server {host}:{port}.""")
    if not os.path.exists(path):
        logger.error(f"Directory does not exist: {path}")
        return errno.ENOENT
    if protocol != 0 and protocol != 1:
        logger.error(f"Invalid protocol: {protocol}. Must be 0 or 1.")
        return errno.EINVAL

    file_name_length = len(file_name)
    if file_name_length > 63:
        logger.error(f"Filename length is {file_name_length}. Must be 1-63 characters long.")
        return errno.EINVAL
    
    file_path = os.path.join(path, file_name)
    if not os.path.isfile(file_path):
        logger.error(f"File not found at path: {file_path}")
        return errno.ENOENT
    
    logger.info(f"File {file_name} found, proceeding with upload.")

    if protocol == 0:
        client_protocol = TCPSAckSender(10, os.path.join(path, file_name), "0.0.0.0", (host, port), 0)
    else:
        client_protocol = stop_and_wait.StopAndWait("0.0.0.0", (host, port), os.path.join(path, file_name))
    logger.info(f"Establishing connection with server")
    client_protocol.establish_connection(Action.UPLOAD.value)
    logger.info(f"Starting file uploading")
    client_protocol.start_upload()

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts a client that uploads a file to a server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity", default= True)
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
    parser.add_argument('-P', '--protocol', action='store', default=0,
                        help="protocol to use (0: TCP + SACK, 1: Stop and Wait)")

    global args
    args = parser.parse_args()
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    upload(args.host, args.port, args.src, args.name, int(args.protocol))
