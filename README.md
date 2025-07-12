# PhyPlus PHY622x platform for [PlatformIO](https://platformio.org)

[![Build Status](https://github.com/cocus/platform-phy622x/workflows/Examples/badge.svg)](https://github.com/cocus/platform-phy622x/actions)

Work in progress for the PhyPlus PHY622X.

# Usage

1. [Install PlatformIO](https://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = phy622x
board = phy6222
framework = phy622x
monitor_speed = 115200
...
```

## Development version

```ini
[env:development]
platform = https://github.com/cocus/platform-phy622x.git
board = phy6222
framework = phy622x
monitor_speed = 115200
...
```

# Configuration

TBD
