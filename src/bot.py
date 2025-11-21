import slixmpp
import ssl
import logging
import asyncio


class MonitorBot(slixmpp.ClientXMPP):
    def __init__(self, jid: str, password: str, admin_jids: list[str], agent_jids: list[str]):
        super().__init__(jid, password)
        self.admin_jids = admin_jids
        self.agent_jids = agent_jids
        self.last_seen = {jid: None for jid in agent_jids}
        self.last_state = {jid: 'up' for jid in agent_jids}
        self.monitoring = True
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("presence", self.presence_handler)
        self.add_event_handler("message", self.message)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        for agent_jid in self.agent_jids:
            self.send_presence_subscription(pto=agent_jid)

    def presence_handler(self, presence):
        entity = str(presence['from'].bare)
        if entity not in self.agent_jids:
            return
        self.last_seen[entity] = asyncio.get_event_loop().time()
        state = self.last_state.get(entity, 'up')
        if presence['type'] == 'unavailable':
            if state != 'down':
                self.last_state[entity] = 'down'
                self.alert_admin(f"[ALERT] Agent {entity} jest NIEDOSTĘPNY (usługa padła)")
        else:
            if state != 'up':
                self.last_state[entity] = 'up'
                status = presence.get('status', '')
                self.alert_admin(f"[RECOVERY] Agent {entity} jest ponownie dostępny: {status}")
            else:
                status = presence.get('status', '')
                logging.info(f"Presence od {entity}: {status}")

    def alert_admin(self, text: str):
        logging.warning(text)
        if not self.monitoring:
            return
        for admin_jid in self.admin_jids:
            self.send_message(
                mto=admin_jid,
                mbody=text,
                mtype='chat'
            )

    def message(self, msg):
        sender = str(msg['from'].bare)
        if sender not in self.admin_jids:
            return
        body = msg['body'].strip().lower()
        if body == "!pause":
            self.send_presence(pshow='away')
            self.monitoring = False
            msg.reply("Monitoring został wstrzymany.").send()
        elif body == "!resume":
            self.send_presence(pshow=None)
            self.monitoring = True
            msg.reply("Monitoring został wznowiony.").send()
        elif body == "!status":
            lines = []
            for agent_jid in self.agent_jids:
                state = self.last_state.get(agent_jid, 'unknown')
                lines.append(f"{agent_jid}: {state.upper()}")
            msg.reply("Status usług:\n" + "\n".join(lines)).send()
        else:
            msg.reply(f"Nie rozumiem...").send()
