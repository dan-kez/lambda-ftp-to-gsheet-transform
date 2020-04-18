from datetime import datetime

from pynamodb.attributes import UTCDateTimeAttribute


def utc_now_wrapper():
    return datetime.utcnow()


class CreatedTimeModelMixin(object):
    # When the column definition was created
    created_time = UTCDateTimeAttribute(default_for_new=utc_now_wrapper)


class UpdateTimeModelMixin(object):
    # When the column definition was created
    updated_time = UTCDateTimeAttribute(default=utc_now_wrapper)

    def save(self, condition=None):
        self.updated_time = utc_now_wrapper()
        return super().save(condition=condition)
