from .mime import MIMEObjectToFileObject
from .triple import TripleToFileObject


def convert_attachment(attachment):
    if isinstance(attachment, tuple):
        return TripleToFileObject(attachment)
    else:
        return MIMEObjectToFileObject(attachment)
