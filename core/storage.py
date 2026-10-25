from django.core.files.storage import storages


def receipt_storage():
    """Separate private storage; files are delivered only by the receipt view."""
    return storages['receipts']
