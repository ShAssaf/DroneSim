import numpy as np
import requests

from src.utils.Consts import Consts
from src.utils.util_classes import ThreeDVector


class EnvironmentAPI:
    @staticmethod
    def get_close_env(pos: ThreeDVector):
        data = {"pos": pos.to_dict()}
        response = requests.post(f"http://127.0.0.1:{Consts.ENV_PORT}/get_close_env", json=data)
        if response.status_code == 200:
            result = np.array(response.json()["close_env_data"])
            return result
        else:
            print("Error:", response.json()["error"])
            return None

    @staticmethod
    def get_env(pos: ThreeDVector):
        data = {"pos": pos.to_dict()}
        response = requests.post(f"http://127.0.0.1:{Consts.ENV_PORT}/get_env", json=data)
        if response.status_code == 200:
            result = np.array(response.json()["env_data"])
            return result
        else:
            print("Error:", response.json()["error"])
            return None
