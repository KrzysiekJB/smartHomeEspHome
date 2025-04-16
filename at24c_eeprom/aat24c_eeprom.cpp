#include "at24c_eeprom.h"
#include "esphome/core/log.h"
#include <cstring> // For memcpy

namespace esphome {
namespace at24c_eeprom {

static const char *const TAG = "at24c_eeprom";

void AT24CEEPROMComponent::setup() {
  ESP_LOGCONFIG(TAG, "Setting up AT24C EEPROM...");
  if (!this->is_ready()) {
    ESP_LOGE(TAG, "AT24C EEPROM not found at address 0x%02X", this->address_);
    this->mark_failed();
    return;
  }
  ESP_LOGCONFIG(TAG, "AT24C EEPROM found at address 0x%02X.", this->address_);
}

void AT24CEEPROMComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "AT24C EEPROM:");
  LOG_I2C_DEVICE(this);
  if (this->is_failed()) {
    ESP_LOGE(TAG, "Connection with AT24C EEPROM failed!");
  }
}

bool AT24CEEPROMComponent::write_byte(uint16_t address, uint8_t data) {
  if (address > 32767) {
    ESP_LOGE(TAG, "Address %u out of range for AT24C256 (0-32767)", address);
    return false;
  }
  uint8_t buffer[3];
  buffer[0] = (address >> 8) & 0xFF;
  buffer[1] = address & 0xFF;
  buffer[2] = data;

  auto err = this->write(buffer, 3);
  if (err != i2c::ERROR_OK) {
    ESP_LOGE(TAG, "Error writing byte to address 0x%04X: I2C Error %d", address, (int)err);
    return false;
  }
  delay(WRITE_CYCLE_DELAY_MS);
  ESP_LOGV(TAG, "Wrote byte 0x%02X to address 0x%04X", data, address);
  return true;
}

bool AT24CEEPROMComponent::read_byte(uint16_t address, uint8_t *data) {
  if (address > 32767) {
    ESP_LOGE(TAG, "Address %u out of range for AT24C256 (0-32767)", address);
    return false;
  }
  uint8_t addr_buffer[2];
  addr_buffer[0] = (address >> 8) & 0xFF;
  addr_buffer[1] = address & 0xFF;

  auto write_err = this->write(addr_buffer, 2, false); // false = no STOP
  if (write_err != i2c::ERROR_OK) {
    ESP_LOGE(TAG, "Error setting read address 0x%04X: I2C Error %d", address, (int)write_err);
    return false;
  }

  auto read_err = this->read(data, 1);
  if (read_err != i2c::ERROR_OK) {
    ESP_LOGE(TAG, "Error reading byte from address 0x%04X: I2C Error %d", address, (int)read_err);
    return false;
  }
  ESP_LOGV(TAG, "Read byte 0x%02X from address 0x%04X", *data, address);
  return true;
}

bool AT24CEEPROMComponent::write_float(uint16_t address, float value) {
  if (address > (32767 - sizeof(float) + 1)) {
    ESP_LOGE(TAG, "Address %u out of range for writing a float (needs %d bytes, max start addr %u)",
             address, (int)sizeof(float), (32767 - sizeof(float) + 1));
    return false;
  }

  uint8_t bytes[sizeof(float)];
  memcpy(bytes, &value, sizeof(float));

  ESP_LOGD(TAG, "Writing float %.4f to address 0x%04X", value, address);
  for (size_t i = 0; i < sizeof(float); ++i) {
    if (!this->write_byte(address + i, bytes[i])) {
      ESP_LOGE(TAG, "Failed to write byte %d of float at address 0x%04X", (int)i, address + i);
      return false;
    }
  }
  ESP_LOGD(TAG, "Successfully wrote float %.4f to address 0x%04X", value, address);
  return true;
}

bool AT24CEEPROMComponent::read_float(uint16_t address, float *value) {
  if (address > (32767 - sizeof(float) + 1)) {
    ESP_LOGE(TAG, "Address %u out of range for reading a float (needs %d bytes, max start addr %u)",
             address, (int)sizeof(float), (32767 - sizeof(float) + 1));
    return false;
  }

  uint8_t bytes[sizeof(float)];
  ESP_LOGD(TAG, "Reading float from address 0x%04X", address);
  for (size_t i = 0; i < sizeof(float); ++i) {
    if (!this->read_byte(address + i, &bytes[i])) {
      ESP_LOGE(TAG, "Failed to read byte %d of float at address 0x%04X", (int)i, address + i);
      return false;
    }
  }

  memcpy(value, bytes, sizeof(float));
  ESP_LOGD(TAG, "Successfully read float %.4f from address 0x%04X", *value, address);
  return true;
}

}  // namespace at24c_eeprom
}  // namespace esphome
