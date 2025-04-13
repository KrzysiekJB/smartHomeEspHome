from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

print("Generuję plik konfiguracyjny do espHome dla rolet")

# Tablica z roletami jako lista słowników
blinds = [
    { "id": "salon_taras", "name": "salon taras", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "salon_FIX", "name": "salon FIX", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "salon_od_sasiada", "name": "salon od sąsiada", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "jadalnia", "name": "jadalnia", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "kuchnia_wyjscie_na_taras", "name": "kuchnia wyjście na taras", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "kuchnia_okno", "name": "kuchnia okno", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "gabinet_parter_okno_lewe", "name": "gabinet parter okno lewe", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "gabinet_parter_okno_prawe", "name": "gabinet parter okno prawe", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_1_16" },
    { "id": "garaz", "name": "garaż", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "pokoj_od_sasiada", "name": "pokój od sąsiada", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "kacperek_okno_lewe", "name": "kacperek okno lewe", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "kacperek_okno_prawe", "name": "kacperek okno prawe", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "sypialnia_prawa", "name": "sypialnia prawa", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "sypialnia_lewa", "name": "sypialnia lewa", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "garderoba_sypialnia", "name": "garderoba sypialnia", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" },
    { "id": "korytarz", "name": "korytarz", "timeUp": "10", "timeDown": "9", "expander": "mcp23017_out_2_32" }
]

# Metoda do zapisywania konfiguracji do pliku
def save_yaml_file(generate_yaml_function, data, filename):

    # Generowanie konfiguracji YAML
    yaml_content = generate_yaml_function(data)

    # Zapis do pliku z użyciem ruamel.yaml
    yaml = YAML()
    # yaml.indent(mapping=2, sequence=2, offset=0)  # Poprawne ustawienia wcięć
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Zapis do pliku
    with open(filename, mode="w", encoding="utf-8") as file:
        yaml.dump(yaml_content, file)

    print(f"Plik {filename} został wygenerowany i zapisany.")

# Metoda generuje switche UP i DOWN do których podłączone są rolety
# Switche ukryte są w HA, steruje tym parametr 'internal': visible_in_ha,
def generate_switches_blinds_yaml(blinds):
    yaml = YAML()
    # yaml.indent(mapping=0, sequence=0, offset=0)  # Ustawienie wcięć dla czytelności

    yaml_config = []  # Lista konfiguracji dla rolet
    pin_number = 1  # Numer pinu startowy
    visible_in_ha = False # Przełącznik nie będzie widoczny w Home Assistant

    for blind in blinds:
        # Tworzenie słownika dla każdej rolety
        blind_config = {
            'platform': 'gpio',
            'name': f"Roleta {blind['name']} UP",
            'pin': {
                'mcp23xxx': f"{blind['expander']}",
                'number': f"${{OUT_RJ45_{pin_number}}}",
                'mode': 'OUTPUT'
            },
            'id': f"relay_{blind['id']}_up",
            'inverted': True,
            'internal': visible_in_ha, 
            'interlock': [f"relay_{blind['id']}_down"],
            'restore_mode': 'ALWAYS_OFF'
        }
        
        yaml_config.append(blind_config)
        blind_config = {
            'platform': 'gpio',
            'name': f"Roleta {blind['name']} DOWN",
            'pin': {
                'mcp23xxx': f"{blind['expander']}",
                'number': f"${{OUT_RJ45_{pin_number + 1}}}",
                'mode': 'OUTPUT'
            },
            'id': f"relay_{blind['id']}_down",
            'inverted': True,
            'internal': visible_in_ha,
            'interlock': [f"relay_{blind['id']}_up"],
            'restore_mode': 'ALWAYS_OFF'
        }
        yaml_config.append(blind_config)
        pin_number += 2  # Zwiększ numer pinu dla kolejnej rolety

    return yaml_config

def generate_eeprom_sensor(blinds):
    yaml_config = []  # Główna sekcja YAML dla EEPROM

    for index, blind in enumerate(blinds, start=1):
        lambda_code = f"return id(eeprom_storage).read_position({index - 1}) * 100.0;"
        
        eeprom_config = {
            'platform': 'template',
            'name': f"Pozycja rolety {blind['name']} z EEPROM",
            'id': f"roleta_position_{blind['id']}_eeprom",
            'unit_of_measurement': '%',
            'accuracy_decimals': 1,
            'lambda': LiteralScalarString(lambda_code),
            'update_interval': '60s'
        }

        yaml_config.append(eeprom_config)

    return yaml_config

# # Metoda generuje konfigurację covers.yaml i prezentuje w HA jako encje rolet
# def generate_covers_yaml(blinds):
#     yaml_config = []  # Główna sekcja YAML dla rolet

#     for index, blind in enumerate(blinds, start=1):
#         cover_config = {
#             'platform': 'time_based',
#             'name': f"Roleta {blind['name']}",
#             'id': f"cover_{blind['id']}",
#             'open_action': [
#                 {'switch.turn_on': f"relay_{blind['id']}_up"},
#                 {'lambda': f"|- id(eeprom_storage).update_position({index - 1}, 1.0); id(roleta_position_eeprom).publish_state(100.0);"}
#             ],
#             'open_duration': f"{blind['timeUp']}s",
#             'close_action': [
#                 {'switch.turn_on': f"relay_{blind['id']}_down"},
#                 {'lambda': f"|- id(eeprom_storage).update_position({index - 1}, 0.0); id(roleta_position_eeprom).publish_state(0.0);"}
#             ],
#             'close_duration': f"{blind['timeDown']}s",
#             'stop_action': [
#                 {'switch.turn_off': f"relay_{blind['id']}_up"},
#                 {'switch.turn_off': f"relay_{blind['id']}_down"},
#                 {'lambda': f"|- float current_position = id(cover_{blind['id']}).position; id(eeprom_storage).update_position({index - 1}, current_position); id(roleta_position_eeprom).publish_state(current_position * 100.0);"}
#             ],
#             'assumed_state': False
#         }
#         yaml_config.append(cover_config)

#     return yaml_config

def generate_covers_yaml(blinds):
    yaml_config = []

    for index, blind in enumerate(blinds, start=1):
        cover_id = f"cover_{blind['id']}"

        open_lambda = LiteralScalarString(
            f"id(eeprom_storage).update_position({index - 1}, 1.0);\n"
            f"id(roleta_position_{blind['id']}_eeprom).publish_state(100.0);"
        )
        close_lambda = LiteralScalarString(
            f"id(eeprom_storage).update_position({index - 1}, 0.0);\n"
            f"id(roleta_position_{blind['id']}_eeprom).publish_state(0.0);"
        )
        stop_lambda = LiteralScalarString(
            f"float current_position = id({cover_id}).position;\n"
            f"id(eeprom_storage).update_position({index - 1}, current_position);\n"
            f"id(roleta_position_{blind['id']}_eeprom).publish_state(current_position * 100.0);"
        )

        cover_config = {
            'platform': 'time_based',
            'name': f"Roleta {blind['name']}",
            'id': cover_id,
            'open_action': [
                {'switch.turn_on': f"relay_{blind['id']}_up"},
                {'lambda': open_lambda}
            ],
            'open_duration': f"{blind['timeUp']}s",
            'close_action': [
                {'switch.turn_on': f"relay_{blind['id']}_down"},
                {'lambda': close_lambda}
            ],
            'close_duration': f"{blind['timeDown']}s",
            'stop_action': [
                {'switch.turn_off': f"relay_{blind['id']}_up"},
                {'switch.turn_off': f"relay_{blind['id']}_down"},
                {'lambda': stop_lambda}
            ],
            'assumed_state': False
        }

        yaml_config.append(cover_config)

    return yaml_config

# Generowanie plików konfiguracyjnych YAML
save_yaml_file(generate_switches_blinds_yaml, blinds, 'switches_blinds.yaml')
save_yaml_file(generate_covers_yaml, blinds, 'covers.yaml')
save_yaml_file(generate_eeprom_sensor, blinds, 'covers_eeprom.yaml')