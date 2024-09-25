import argparse
import logging
import os
import protocol
from action import Action

logger = logging.getLogger(__name__)


def download(host: str, port: int, path: str, file_name: str):
    logger.info(f"""Starting client downloading file {file_name} into location {path} 
        from server {host}:{port}.""")
    if not os.path.exists(path):
         os.makedirs(path)  # TODO: Should handle errors
    client_protocol = protocol.StopAndWait("localhost", (host, port), os.path.join(path, file_name))
    logger.info(f"Stablishing connection with server")
    client_protocol.stablish_connection(Action.DOWNLOAD.value)
    logger.info(f"Starting file uploading")
    client_protocol.start_download()
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts a client that downloads a file from a server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="decrease output verbosity")
    parser.add_argument('-H', '--host', action='store', default="localhost",
                        help="server IP address")
    parser.add_argument('-p', '--port', action='store', default=12345,
                        help="server port")
    parser.add_argument('-d', '--dst', action='store', default="./files/client_storage",
                        help="destination file path")
    parser.add_argument('-n', '--name', action='store', default="file.txt",
                        help="file name")

    args = parser.parse_args()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    download(args.host, args.port, args.dst, args.name)
