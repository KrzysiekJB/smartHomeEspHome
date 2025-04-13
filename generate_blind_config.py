from ruamel.yaml import YAML

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

def generate_blinds_yaml(blinds):
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

# Generowanie konfiguracji YAML
yaml_content = generate_blinds_yaml(blinds)

# Zapis do pliku z użyciem ruamel.yaml
yaml = YAML()
yaml.indent(mapping=2, sequence=2, offset=0)  # Poprawne ustawienia wcięć

# Opcja 1: Zapis do pliku
with open("espHome_blinds.yaml", mode="w", encoding="utf-8") as file:
    yaml.dump(yaml_content, file)
print("Plik espHome_blinds.yaml został wygenerowany i zapisany.")
