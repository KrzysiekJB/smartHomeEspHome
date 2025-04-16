import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c
from esphome.const import CONF_ADDRESS, CONF_ID, CONF_I2C_ID
from esphome.core import CORE

# Namespace
at24c_ns = cg.esphome_ns.namespace('at24c_eeprom')
At24cEeprom = at24c_ns.class_('AT24CEEPROMComponent', cg.Component, i2c.I2CDevice)

# Konfiguracja
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(At24cEeprom),
    # Użyj standardowego schematu urządzenia I2C
}).extend(i2c.i2c_device_schema(default_address=0x50))
# USUNIĘTO -> .extend(cv.polling_component_schema('1s'))

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)
    # Nie ma potrzeby ustawiania adresu ręcznie, robi to I2CDevice