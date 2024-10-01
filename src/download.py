import argparse
import errno
import logging
import os
from lib.protocols.stop_and_wait import stop_and_wait
from lib.utils.action import Action
from lib.protocols.TCP_SACK.tcp_sack_receiver import TCPSAckKReceiver

logger = logging.getLogger(__name__)


def download(host: str, port: int, path: str, file_name: str,
             protocol: int) -> int:
    logger.info(
        f"Starting client downloading file {file_name} into location {path} "
        f"from server {host}:{port}.")
    if not os.path.exists(path):
        os.makedirs(path)  # TODO: Should handle errors
    if protocol != 0 and protocol != 1:
        logger.error(f"Invalid protocol: {protocol}. Must be 0 or 1.")
        return errno.EINVAL
    file_name_length = len(file_name)
    if file_name_length > 63:
        logger.error(
            f"Filename length is {file_name_length}. "
            f"Must be 1-63 characters long.")
        return errno.EINVAL

    if protocol == 0:
        client_protocol = TCPSAckKReceiver(100, os.path.join(path, file_name),
                                           "0.0.0.0", (host, port), 0)
    else:
        client_protocol = stop_and_wait.StopAndWait("0.0.0.0", (host, port),
                                                    os.path.join(path,
                                                                 file_name))
    logger.info("Establishing connection with server")
    if client_protocol.establish_connection(Action.DOWNLOAD.value):
        logger.info("Starting file download")
        client_protocol.start_download(None)
        return 0
    return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts a client that downloads a file from a server",
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
    parser.add_argument('-d', '--dst', action='store',
                        default="./files/client_storage",
                        help="destination file path")
    parser.add_argument('-n', '--name', action='store',
                        default="T-rex.jpg",
                        help="file name")
    parser.add_argument('-P', '--protocol', action='store', default=0,
                        help="protocol to use (0: TCP+SACK, 1: Stop and Wait)")

    args = parser.parse_args()
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    download(args.host, args.port, args.dst, args.name, int(args.protocol))
