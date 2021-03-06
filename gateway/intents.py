# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
import functools


def _has_intent(v: int, i: int):
    return True if v & i else False


class Intents:
    def __init__(self, session_intents: int):
        has = functools.partial(_has_intent, session_intents)
        self.direct_messages = has(1 << 0)
        self.presences = has(1 << 1)
        self.guilds = has(1 << 2)
        self.guild_channels = has(1 << 3)
        self.guild_members = has(1 << 4)
        self.guild_messages = has(1 << 5)

if __name__ == '__main__':
    print(1 << 1 | 1 << 2)
