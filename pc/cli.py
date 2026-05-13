import time
from agentspace import Agent, space


class CLI(Agent):
    def __init__(self, command_name="snapshot_cmd"):
        self.command_name = command_name
        super().__init__()

    def init(self):
        time.sleep(2)  # let mirrors connect and print their status first
        self.trigger()

    def senseSelectAct(self):
        try:
            name = input("\nObject name to snapshot (empty to skip, Ctrl-D to quit): ").strip()
        except EOFError:
            print("\n[CLI] exiting")
            self.stop()
            return
        if name:
            space[self.command_name] = name
            time.sleep(0.2)  # let the snapshotter print its result first
        self.trigger()