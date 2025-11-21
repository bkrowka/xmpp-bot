import slixmpp
import ssl
import asyncio
import subprocess
import logging as log


class ServiceAgent(slixmpp.ClientXMPP):
    def __init__(self, jid: str, password: str, service_name: str):
        super().__init__(jid, password)
        self.service_name = service_name
        self.last_state = None

        self.add_event_handler("session_start", self.start)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def start(self, event) -> None:
        self.send_presence()
        await asyncio.create_task(self.monitor())

    def check(self) -> bool:
        try:
            p = subprocess.run(
                ["systemctl", "is-active", self.service_name],
                capture_output=True,
                text=True,
                check=False,
            )
            return p.stdout.strip() == "active"
        except Exception:
            log.exception("Failed to check service state")
            return False

    async def monitor(self) -> None:
        while True:
            ok = self.check()
            state = "available" if ok else "unavailable"

            if state != self.last_state:
                if ok:
                    self.send_presence(pshow=None, pstatus=f"{self.service_name} OK")
                else:
                    self.send_presence(pshow="dnd", pstatus=f"{self.service_name} DOWN")
                log.info("Agent %s: %s", self.service_name, state)
                self.last_state = state
            await asyncio.sleep(5)
