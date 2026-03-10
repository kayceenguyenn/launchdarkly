import ldclient
from ldclient.config import Config
from dotenv import load_dotenv
import os

load_dotenv()


def init_ld_client():
    ldclient.set_config(Config(os.getenv("LD_SDK_KEY")))
    client = ldclient.get()
    if not client.is_initialized():
        raise RuntimeError("LaunchDarkly client failed to initialize")
    return client


ld_client = init_ld_client()
