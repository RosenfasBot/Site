from django.conf import settings
from django.contrib.staticfiles.storage import (
    ManifestStaticFilesStorage, StaticFilesStorage,
)
from .models import Gerencial
import requests

class MyManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def file_hash(self, name, content=None):
        return None

def SendTelegramMessage(chat_id, message):
    TOKEN = Gerencial.load().telegram_bottoken
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
    res = requests.post(api_url, data=params)
    return res.status_code