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

def generate_covers_yaml(blinds):
    yaml_config = []

    # Zakładamy, że float zajmuje 4 bajty, int zajmuje 1 bajt
    bytes_per_position = 1

    for index, blind in enumerate(blinds):
        cover_id = f"cover_{blind['id']}"
        # Oblicz unikalny adres dla każdej rolety
        save_address = index * bytes_per_position

        open_lambda = LiteralScalarString(
            f"id(eeprom_storage).update_position({index - 1}, 1.0);\n"
            f"id(roleta_position_{blind['id']}_eeprom).publish_state(100.0);"
        )
        close_lambda = LiteralScalarString(
            f"id(eeprom_storage).update_position({index - 1}, 0.0);\n"
            f"id(roleta_position_{blind['id']}_eeprom).publish_state(0.0);"
        )

        # Przykład dla float
        # stop_lambda = LiteralScalarString(
        #     f"float current_pos = id({cover_id}).position;\n"
        #     f"uint16_t save_address = {save_address};\n"
        #     f"ESP_LOGD(\"cover_save\", \"Roleta {blind['name']} zatrzymana. Pozycja: %.2f. Zapis do EEPROM (addr %u)...\", current_pos, save_address);\n"
        #     f"if (id(eeprom_storage).write_float(save_address, current_pos)) {{\n"  # Zwróć uwagę na {{
        #     f"  ESP_LOGD(\"cover_save\", \"Zapisano pozycję %.2f do EEPROM pod adresem %u.\", current_pos, save_address);\n" # Zwróć uwagę na ręczne wcięcie "  " i \"
        #     # f"  // Opcjonalna linia...\n" # Dodawanie komentarzy też wymagałoby osobnej linii f-string
        #     f"}} else {{\n" # Zwróć uwagę na }} i {{
        #     f"  ESP_LOGE(\"cover_save\", \"Błąd zapisu pozycji do EEPROM pod adresem %u!\", save_address);\n" # Ręczne wcięcie i \"
        #     f"}}" # Zwróć uwagę na }}
        # )

        # Zapis w INT
        # ---- Generowanie stop_lambda w żądanym (mniej czytelnym) stylu ----
        stop_lambda = LiteralScalarString(
            f"// Pobierz pozycję jako float (0.0 - 1.0)\n"
            f"float current_pos_float = id({cover_id}).position;\n"
            f"// Przekonwertuj na procent (0-100) i zaokrąglij do najbliższej liczby całkowitej\n"
            f"uint8_t current_pos_int = (uint8_t)round(current_pos_float * 100.0);\n"
            f"// Upewnij się, że wartość jest w zakresie 0-100\n"
            f"if (current_pos_int > 100) {{ current_pos_int = 100; }}\n" # Użycie {{ }} dla literałów { }
            f"\n" # Pusta linia dla czytelności w C++ (opcjonalnie)
            f"uint16_t save_address = {save_address};\n"
            f"ESP_LOGD(\"cover_save\", \"Roleta {blind['name']} zatrzymana. Pozycja: %.2f (int: %u). Zapis do EEPROM (addr %u)...\", current_pos_float, current_pos_int, save_address);\n" # Użycie \" dla cudzysłowów
            f"\n" # Pusta linia
            f"// Zapisz pojedynczy bajt (uint8_t) do EEPROM\n"
            f"if (id(eeprom_storage).write_byte(save_address, current_pos_int)) {{\n" # Użycie {{
            f"  ESP_LOGD(\"cover_save\", \"Zapisano pozycję (int %u) do EEPROM pod adresem %u.\", current_pos_int, save_address);\n" # Ręczne wcięcie "  " i \"
            # Opcjonalne publikowanie stanu - wymagałoby kolejnej linii f-string z wcięciem
            # f"  // id(roleta_position_{blind['id']}_eeprom).publish_state(current_pos_float * 100.0);\n"
            f"}} else {{\n" # Użycie }} i {{
            f"  ESP_LOGE(\"cover_save\", \"Błąd zapisu pozycji (int %u) do EEPROM pod adresem %u!\", current_pos_int, save_address);\n" # Ręczne wcięcie "  " i \"
            f"}}" # Użycie }} na końcu, bez \n
        )
        
        cover_config = {
            'platform': 'time_based',
            'name': f"Roleta {blind['name']}",
            'id': cover_id,
            'open_action': [
                {'switch.turn_on': f"relay_{blind['id']}_up"}
                # {'lambda': open_lambda}
            ],
            'open_duration': f"{blind['timeUp']}s",
            'close_action': [
                {'switch.turn_on': f"relay_{blind['id']}_down"}
                #{'lambda': close_lambda}
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