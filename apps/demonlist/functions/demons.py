from django.db.models import Func

class ExtractUUID(Func):
    function = 'SUBSTRING'
    template = (
        "%(function)s("
        "%(expressions)s FROM 31 FOR "
        "GREATEST("
        "COALESCE(NULLIF(POSITION('?' IN %(expressions)s), 0) - 31, LENGTH(%(expressions)s) - 30), 0)"
        ")"
    )
