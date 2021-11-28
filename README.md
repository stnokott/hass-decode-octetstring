## Home Assistant component to decode Octet String values from other sensors

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

### Configuration
- Create a sensor entry in your `configuration.yaml` like this:
```Configuration.yaml:
  sensor:
    - platform: octetstringdecode
      name: "Decoded sensor name"               (required)
      entity_id: "sensor.octet_string_sensor"   (required)
```