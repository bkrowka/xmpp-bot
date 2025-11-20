import os
import argparse
import logging

from dotenv import load_dotenv
from src.utils import get_required_env
from src.bot import EchoBot


def run() -> None:
    load_dotenv()
    jid = get_required_env("BOT_JID")
    password = get_required_env("BOT_PASSWORD")
    host = os.environ.get("XMPP_HOST", "localhost")
    port = int(os.environ.get("XMPP_PORT", 5222))
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)-8s %(message)s')
    bot = EchoBot(jid, password)
    bot.connect((host, port))
    try:
        bot.process(forever=True)
    except KeyboardInterrupt:
        bot.disconnect()


if __name__ == "__main__":
    run()
