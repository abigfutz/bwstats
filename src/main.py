import requests
from enum import StrEnum, auto
from typing import Any


from pydantic import BaseModel
from dotenv import dotenv_values


class InvalidAPIKeyError(Exception):
    pass


class NoBedwarsStatsError(Exception):
    pass


class APIThrottleError(Exception):
    pass


class BedwarsMode(StrEnum):
    OVERALL = auto()
    EIGHT_ONE = auto()
    EIGHT_TWO = auto()
    FOURS_THREE = auto()
    FOURS_FOUR = auto()


class BedwarsStats(BaseModel):
    final_kills_bedwars: int
    final_deaths_bedwars: int
    kills_bedwars: int
    deaths_bedwars: int
    beds_broken_bedwars: int
    beds_lost_bedwars: int
    wins_bedwars: int
    losses_bedwars: int


class Bedwars:
    def __init__(self, api_key: str, player_name: str) -> None:
        self._key = api_key
        self.player_name = player_name
        self._response = self._handle_request()

    def _handle_request(self) -> requests.Response:
        response = requests.get(
            "https://api.hypixel.net/player",
            params={"name": self.player_name},
            headers={"API-Key": self._key}
        )
        
        if response.status_code == 403:
            raise InvalidAPIKeyError("Please provide a valid API key.")
        elif response.status_code == 429:
            raise APIThrottleError(
                "Please wait two minutes before calling the API with the same player name."
            )

        
        return response

    def stats(self, mode: BedwarsMode) -> BedwarsStats:
        json = self._response.json()
        stats = json.get("player", {}).get("stats", {}).get("Bedwars")
        if stats is None:
            raise NoBedwarsStatsError(f"Player '{self.player_name}' hasn't played bedwars.")
        
        fields = BedwarsStats.__fields__.keys()
        
        if mode == BedwarsMode.OVERALL:
            return BedwarsStats(**{field: stats.get(field) for field in fields})
        
        true_stats = {
            field: stats.get(f"{mode}_{field}")
            for field in fields
        }

        return BedwarsStats(**true_stats)


if __name__ == "__main__":
    env = dotenv_values(".env")
    key = env["API_KEY"]
    if key is None:
        exit(-1)

    bw = Bedwars(key, "Fuhts")
    print(bw.stats(BedwarsMode.OVERALL))