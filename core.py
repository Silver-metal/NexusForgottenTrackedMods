import json, API


def get_game_name():
    return domains_to_names[game_domain_name]


def get_game_domain(name):
    return names_to_domains[name]


def change_game_domain(name):
    global game_domain_name
    game_domain_name = get_game_domain(name)
    global mod_names
    mod_names['default'] = game_domain_name
    jstring = json.dumps(mod_names)
    with open('data.json', 'w') as file:
        file.write(jstring)

def get_non_downloaded_mods():
    tracked_ids = get_tracked_ids()
    endorsed_ids = get_endorsed_ids()
    read_configs()
    return [(x, get_mod_url(x), get_mod_name(x)) for x in tracked_ids if x not in endorsed_ids]


def get_tracked_ids():
    tracked_mods = API.get_tracked_mods()
    return [x["mod_id"] for x in tracked_mods if (x["domain_name"] == game_domain_name)]


def get_endorsed_ids():
    endorsed_mods = API.get_endorsed_mods()
    return [x["mod_id"] for x in endorsed_mods if (x["domain_name"] == game_domain_name)]


def get_mod_url(mod_id):
    return "https://www.nexusmods.com/{game_domain_name}/mods/{mod_id}".format(game_domain_name=game_domain_name,
                                                                               mod_id=mod_id)


def get_mod_data(mod_id):
    mod_data = API.get_mod_data(game_domain_name, mod_id)
    try:
        name = mod_data['name']
    except:
        name = 'DELETED'
    save_configs(mod_id, name)
    return mod_data


def get_mod_name(mod_id):
    try:
        return mod_names[game_domain_name][str(mod_id)]
    except:
        return ''


def read_configs():
    global mod_names
    try:
        with open('data.json') as file:
            mod_names = json.load(file)
    except json.decoder.JSONDecodeError:
        with open('data.json', 'w') as file:
            file.write(json.dumps(mod_names))



def save_configs(mod_id, mod_name):
    mod_names[game_domain_name][str(mod_id)] = mod_name
    jstring = json.dumps(mod_names)
    with open('data.json', 'w') as file:
        file.write(jstring)


games_list = API.get_games_list()

mod_names = {}
domains_to_names = {}
names_to_domains = {}
for game in games_list:
    domains_to_names[game['domain_name']] = game['name']
    names_to_domains[game['name']] = game['domain_name']
    mod_names[game['domain_name']] = {}

read_configs()
try:
    game_domain_name = mod_names['default']
except KeyError:
    game_domain_name = 'skyrimspecialedition'
game_name = domains_to_names[game_domain_name]
