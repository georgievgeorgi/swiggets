import datetime
from string import Template


class timedelta(datetime.timedelta):
    def __format__(self, format_spec, /):
        class DeltaTemplate(Template):
            delimiter = "%"
        f = DeltaTemplate(format_spec)

        secs_total = self.total_seconds()
        hours_total, rem = divmod(secs_total, 60*60)
        mins_total, rem = divmod(secs_total, 60)
        days, rem = divmod(secs_total, 24*60*60)
        hours, rem = divmod(rem, 60*60)
        mins, secs = divmod(rem, 60)

        return f.substitute(
            d="{:d}".format(int(days)),
            h="{:01d}".format(int(hours_total)),
            H="{:02d}".format(int(hours)),
            m="{:04d}".format(int(mins_total)),
            M="{:02d}".format(int(mins)),
            S="{:02d}".format(int(secs)),
            s="{:05d}".format(int(secs_total)),
        )
