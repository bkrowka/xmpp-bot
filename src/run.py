import argparse
import logging

from getpass import getpass
from src.bot import EchoBot


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jid", required=True, help="JID")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--host", default="localhost", help="XMPP server address")
    parser.add_argument("--port", type=int, default=5222, help="XMPP server port")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)-8s %(message)s')
    bot = EchoBot(args.jid, args.password)
    bot.connect((args.host, args.port))
    try:
        bot.process(forever=True)
    except KeyboardInterrupt:
        bot.disconnect()


if __name__ == "__main__":
    run()
