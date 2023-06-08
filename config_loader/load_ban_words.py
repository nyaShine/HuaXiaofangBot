import json


class BanWordConfig:
    def __init__(self, id: int, enabled: bool, notify: bool, muteTime: int, deleteUser: bool, words: list):
        self.id = id
        self.enabled = enabled
        self.notify = notify
        self.muteTime = muteTime
        self.deleteUser = deleteUser
        self.words = words


def load_ban_words(filename: str) -> list[BanWordConfig]:
    ban_configs = []

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

        for config in data["configurations"]:
            ban_configs.append(BanWordConfig(
                config["id"],
                config["enabled"],
                config["notify"],
                config["muteTime"],
                config["deleteUser"],
                config["words"]
            ))

    return ban_configs
