import requests
import APIKey

headers = {'apikey': APIKey.key} # For development purposes, add your personal key in the corresponding file
base_url = "https://api.nexusmods.com"
tracked_mods_url = base_url + "/v1/user/tracked_mods.json"
endorsements_url = base_url + "/v1/user/endorsements.json"
games_url = base_url + "/v1/games.json"
mod_url = base_url + "/v1/games/{game_domain_name}/mods/{id}.json"


def get_tracked_mods():
    return requests.get(tracked_mods_url, headers=headers).json()


def get_games_list():
    return requests.get(games_url, headers=headers).json()


def get_endorsed_mods():
    return requests.get(endorsements_url, headers=headers).json()


def get_mod_data(domain, mod_id):
    return requests.get(mod_url.format(game_domain_name=domain, id=mod_id), headers=headers).json()
