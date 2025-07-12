# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

"""

import glob
import os
import string

from SCons.Script import DefaultEnvironment

from platformio.builder.tools.piolib import PlatformIOLibBuilder

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
mcu = board.get("build.mcu", "")
product_line = board.get("build.product_line", "")
assert product_line, "Missing MCU or Product Line field"

env.SConscript("_bare.py")

NO_OSAL_DIR = platform.get_package_dir("framework-phy622x")
assert os.path.isdir(NO_OSAL_DIR)

class CustomLibBuilder(PlatformIOLibBuilder):

    def build(self):
        if self.env.GetBuildType() == "debug":
            self.env.ConfigureDebugFlags()
        return PlatformIOLibBuilder.build(self)

def build_custom_lib(lib_path, lib_manifest=None):
    if not os.path.isdir(lib_path):
        return
    if lib_path:
        lib_manifest = lib_manifest or {"name": os.path.basename(lib_path)}
        env.Append(
            EXTRA_LIB_BUILDERS=[
                CustomLibBuilder(env, lib_path, lib_manifest.copy())
            ]
        )

def build_bsp_lib():
    # Note: config files for USB peripheral is located in project dirs
    manifest = {
        "name": "phy622x-bsp",
        "build": {
            "flags": ["-I $PROJECT_SRC_DIR", "-I $PROJECT_INCLUDE_DIR"],
            "srcFilter": [
                "-<*>",
                "+<osal_nuker.c>",
                "+<log/log.c>",
                "+<jump_table.c>",
                "+<%s>" % os.path.join("ble", "rf", "patch.c"),
                "+<%s>" % os.path.join("ble", "controller", "rf_phy_driver.c")
            ],
        }
    }

    bsp_dir = os.path.join(NO_OSAL_DIR, "bsp")
    if not os.path.isdir(bsp_dir):
        print("Error! bsp dir not found?")
        assert False

    # "timer", "spiflash"
    for s in ["adc", "aes", "clock", "dma", "flash", "gpio", "i2c", "pwm", "pwrmgr", "spi", "uart"]:
        manifest['build']['srcFilter'].extend([" +<%s.c>" % os.path.join(bsp_dir, "driver", s, s)])

    build_custom_lib(bsp_dir, manifest)


def build_freertos_lib():
    # Note: config files for USB peripheral is located in project dirs
    manifest = {
        "name": "phy622x-freertos",
        "build": {
            "flags": [ "-I $PROJECT_SRC_DIR", "-I $PROJECT_INCLUDE_DIR" ],
            "srcFilter": [
                "-<*>",
                "+<*.c>",
                "+<portable/GCC/ARM_CM0/port.c>",
                "+<portable/GCC/ARM_CM0/portasm.c>",
                "+<portable/MemMang/heap_4.c>"
            ],
        }
    }

    freertos_dir = os.path.join(NO_OSAL_DIR, "freertos")
    if not os.path.isdir(freertos_dir):
        print("Error! freertos dir not found?")
        assert False

    build_custom_lib(freertos_dir, manifest)

def get_linker_script():
    default_ldscript = os.path.join(
        NO_OSAL_DIR, "bsp", "%s.ld" % mcu)

    if not os.path.isfile(default_ldscript):
        print("Errror! Cannot find a linker script for the required board! ")
        assert False

    return default_ldscript

def prepare_startup_file(src_path):
    startup_file = os.path.join(src_path, "%s_start.S" % mcu)
    # Change file extension to uppercase:
    if not os.path.isfile(startup_file) and os.path.isfile(startup_file[:-2] + ".s"):
        os.rename(startup_file[:-2] + ".s", startup_file)
    if not os.path.isfile(startup_file):
        print("Warning! Cannot find the default startup file for %s. "
              "Ignore this warning if the startup code is part of your project." % mcu)

#
# Allow using custom linker scripts
#

if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=get_linker_script())

#
# Prepare build environment
#

# The final firmware is linked against standard library with two specifications:
# nano.specs - link against a reduced-size variant of libc
# nosys.specs - link against stubbed standard syscalls

env.Append(
    CPPPATH=[
        "$PROJECT_SRC_DIR",
        "$PROJECT_INCLUDE_DIR",
        os.path.join(NO_OSAL_DIR, "freertos"),
        os.path.join(NO_OSAL_DIR, "freertos", "include"),
        os.path.join(NO_OSAL_DIR, "freertos", "portable", "GCC", "ARM_CM0"),
        os.path.join(NO_OSAL_DIR, "bsp"),
        os.path.join(NO_OSAL_DIR, "bsp", "CMSIS", "include"),
        os.path.join(NO_OSAL_DIR, "bsp", "CMSIS", "device", "phyplus")
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs",
        "-Wl,--just-symbols=%s" % os.path.join(NO_OSAL_DIR, "bsp", "symbols", "%s_rom.gcc" % mcu)
    ]
)

#
# FreeRTOS lib
#
#if "freertos" in env.subst("$PIOFRAMEWORK"):
build_freertos_lib()
env.Append(CPPDEFINES=[ "ENABLE_FREERTOS" ])
#
# BSP libraries
#
build_bsp_lib()

#
# Compile CMSIS/startup sources
#

sources_path = os.path.join(NO_OSAL_DIR, "bsp", "CMSIS", "device", "phyplus")
prepare_startup_file(sources_path)

env.BuildSources(
    os.path.join("$BUILD_DIR", "phy-cmsis-startup"), sources_path,
    src_filter=[
        "-<*>",
        "+<%s>" % board.get("build.cmsis.system_file", "%s_cstart.c" % mcu),
        "+<%s>" % board.get("build.cmsis.startup_file", "%s_start.S" % mcu)
    ]
)
