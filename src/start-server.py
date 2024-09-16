import argparse
import logging

logger = logging.getLogger(__name__)


def start_server(host: str, port: str, storage: str) -> None:
    logger.info(f"Starting server on {host}:{port} with storage at {storage}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts File Transfer Server")

    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="decrease output verbosity")
    parser.add_argument('-H', '--host', action='store',
                        help="service IP address", metavar="\b")
    parser.add_argument('-p', '--port', action='store',
                        help="service port", metavar="\b")
    parser.add_argument('-s', '--storage', action='store',
                        help="storage dir path", metavar="\b")

    args = parser.parse_args()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    start_server(args.host, args.port, args.storage)
