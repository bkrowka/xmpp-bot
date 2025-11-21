import os
import argparse
import logging
import asyncio

from dotenv import load_dotenv
from src.utils import get_required_env, load_config
from src.agent import ServiceAgent
from src.bot import MonitorBot


def run() -> None:
    load_dotenv()
    jid = get_required_env("BOT_JID")
    password = get_required_env("BOT_PASSWORD")
    host = os.environ.get("XMPP_HOST", "localhost")
    port = int(os.environ.get("XMPP_PORT", 5222))
    config = load_config(os.path.join("config.json"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)-8s %(message)s')
    admin_jids = [admin["jid"] for admin in config["admins"]]
    agent_map = {}
    agents = []
    for svc in config["services"]:
        agent_map[svc["jid"]] = svc["name"]
        agent = ServiceAgent(
            jid=svc['jid'],
            password=svc['password'],
            service_name=svc['name']
        )
        agent.connect((host, port))
        agents.append(agent)
    bot = MonitorBot(jid, password, admin_jids, agent_map)
    bot.connect((host, port))
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        bot.disconnect()
        for agent in agents:
            agent.disconnect()


if __name__ == "__main__":
    run()
