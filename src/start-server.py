import argparse
import logging
import os
#import protocol.udp_client as udp_client
import accepter as accepter

logger = logging.getLogger(__name__)


def start_server(host: str, port: int, storage: str) -> None:
    if not os.path.exists(storage):
        os.makedirs(storage)  # TODO: Should handle errors
    logger.info(f"Starting server on {host}:{port} with storage at {storage}.")
    clients_threads = []
    server_accepter = accepter.Accepter(storage, host, port)
    while True:
        new_client = server_accepter.receive_client()
        new_client.start()
        clients_threads.append(new_client)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts File Transfer Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="decrease output verbosity")
    parser.add_argument('-H', '--host', action='store', default="localhost",
                        help="service IP address")
    parser.add_argument('-p', '--port', action='store', default=12345,
                        help="service port")
    parser.add_argument('-s', '--storage', action='store', default="./files/server_storage",
                        help="storage dir path")

    args = parser.parse_args()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    start_server(args.host, args.port, args.storage)
