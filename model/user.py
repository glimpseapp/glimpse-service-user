import time
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.util import datetime_from_timestamp


def date_now():
    return datetime_from_timestamp(time.time())


class UserInfoById(Model):
    user_id = columns.Text(primary_key=True)
    username = columns.Text(required=False)
    email = columns.Text(required=False)
    create_date = columns.DateTime(default=date_now)  # rename to creation_date

    def to_object(self):
        return {
            'user_id': str(self.user_id),
            'username': self.username,
            'email': self.email,
            'create_date': self.create_date.isoformat()
        }


class UserInfoByUsername(Model):
    username = columns.Text(primary_key=True)
    user_id = columns.Text()

    def to_object(self):
        return {
            'user_id': str(self.user_id),
            'username': self.username,
        }
