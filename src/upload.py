import argparse
import logging
import os
import errno


logger = logging.getLogger(__name__)


def upload(host: str, port: str, path: str, file_name: str):
    logger.info(f"""Starting client uploading file {file_name} at location {path} 
        to server {host}:{port}.""")
    if not os.path.exists(path):
        logger.error(f"Directory does not exist: {path}")
        return errno.ENOENT
    
    file_path = os.path.join(path, file_name)
    if not os.path.isfile(file_path):
        logger.error(f"File not found at path: {file_path}")
        return errno.ENOENT
    
    logger.info(f"File {file_name} found, proceeding with upload.")
    # TODO: Add upload logic here
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
    parser.add_argument('-H', '--host', action='store', default="localhost",
                        help="server IP address")
    parser.add_argument('-p', '--port', action='store', default="12345",
                        help="server port")
    parser.add_argument('-s', '--src', action='store', default="./client_storage",
                        help="source file path")
    parser.add_argument('-n', '--name', action='store', default="./file.txt",
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
