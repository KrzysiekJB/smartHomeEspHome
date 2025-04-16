#pragma once

#include "esphome/core/component.h"
#include "esphome/components/i2c/i2c.h"

namespace esphome {
namespace at24c_eeprom {

static const uint16_t WRITE_CYCLE_DELAY_MS = 5; // ms

class AT24CEEPROMComponent : public Component, public i2c::I2CDevice {
 public:
  void setup() override;
  void dump_config() override;

  // Zapis pojedynczego bajtu
  bool write_byte(uint16_t address, uint8_t data);

  // Odczyt pojedynczego bajtu
  bool read_byte(uint16_t address, uint8_t *data);

  // Zapis float (4 bajty)
  bool write_float(uint16_t address, float value);

  // Odczyt float (4 bajty)
  bool read_float(uint16_t address, float *value);
};

}  // namespace at24c_eeprom
}  // namespace esphome
