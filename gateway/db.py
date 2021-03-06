# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
import os
from time import time
from typing import Any

import dotenv
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection, management, models, usertype

dotenv.load_dotenv()
auth_provider = PlainTextAuthProvider(
    os.getenv('client_id'), os.getenv('client_secret')
)


def connect():
    try:
        if os.getenv('safe', 'false') == 'true':
            cloud = {
                'secure_connect_bundle': os.getcwd() + r'/gateway/static/bundle.zip'
            }
            connection.setup(
                [],
                'airbus',
                cloud=cloud,
                auth_provider=auth_provider,
                connect_timeout=200,
            )
        else:
            connection.setup(
                [],
                'airbus',
                auth_provider=auth_provider,
                connect_timeout=200,
            )
        connection.get_session().execute('USE airbus;')
    except:
        connect()


class Presence(models.Model):
    __options__ = {'gc_grace_seconds': 43200}
    user_id = columns.BigInt(primary_key=True)
    since = columns.Float(default=time)
    status = columns.Text(default='offline')
    afk = columns.Boolean(default=False)
    description = columns.Text(max_length=40, default='')
    bold = columns.Text(max_length=6, default='')
    type = columns.Integer(default=0)
    stay_offline = columns.Boolean(default=False)


def to_dict(model: models.Model) -> dict:
    initial: dict[str, Any] = model.items()
    ret = dict(initial)

    for name, value in initial:
        if isinstance(value, (usertype.UserType, models.Model)):
            # things like member objects or embeds can have usertypes 3/4 times deep
            # there shouldnt be a recursion problem though
            value = dict(value.items())
            for k, v in value.items():
                if isinstance(v, usertype.UserType):
                    value[k] = to_dict(v)
            ret[name] = value

        # some values are lists of usertypes
        elif isinstance(value, (list, set)):
            if isinstance(value, set):
                value = list(value)

            set_values = []

            for v in value:
                if isinstance(v, usertype.UserType):
                    set_values.append(to_dict(v.items()))
                else:
                    set_values.append(v)

            ret[name] = set_values

        if name == 'id' or name.endswith('_id') and len(str(value)) > 14:
            ret[name] = str(value)
        if name == 'permissions':
            ret[name] = str(value)

    return ret


if __name__ == '__main__':
    connect()
    management.sync_table(Presence)
