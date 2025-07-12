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

import os
import sys
import subprocess

from platformio.managers.platform import PlatformBase
from platformio.project.helpers import get_project_dir


IS_WINDOWS = sys.platform.startswith("win")


class Phy622xPlatform(PlatformBase):

    def generate_sample_code(self, project_config, environment):
        framework = project_config.get(f"env:{environment}", "framework", None)
        if framework != ["phy622x"]:
            return

        src_dir = project_config.get("platformio", "src_dir")

        # os.getcwd() == CURRENT_PROJECT_DIR
        main_path = os.path.join(src_dir, "main.c")
        freertos_config_path = os.path.join(src_dir, "FreeRTOSConfig.h")

        # if project was previously generated
        if os.path.isfile(main_path) and os.path.isfile(freertos_config_path):
            return

        main_content = """
#include "osal_nuker.h"
#include <log/log.h>

int main(void)
{
    /* init stuff as if OSAL was in charge */
    osal_nuker_init(SYS_CLK_DLL_96M, CLK_32K_RCOSC);

    LOG("Hello!");

    /* Do something here! */
    return 0;
}

"""
        freertos_config_content = """
/*
 * FreeRTOS Kernel <DEVELOPMENT BRANCH>
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * https://www.FreeRTOS.org
 * https://github.com/FreeRTOS
 *
 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/******************************************************************************/
/* Hardware description related definitions. **********************************/
/******************************************************************************/

#include <stdint.h>
extern uint32_t sysclk_get_clk(void);
#define configCPU_CLOCK_HZ    ( ( unsigned long ) sysclk_get_clk() )

#include <log/log.h>
#define configASSERT( x )         \\
    if( ( x ) == 0 )              \\
    {                             \\
        LOG("ASSERTION FAILED: %s, %d", __FILE__, __LINE__); \\
        taskDISABLE_INTERRUPTS(); \\
        for( ; ; )                \\
        ;                         \\
    }

/* Definitions that map the FreeRTOS port interrupt handlers to their CMSIS
standard names. */
#define vPortSVCHandler    SVC_Handler
#define xPortPendSVHandler PendSV_Handler

/******************************************************************************/
/* Scheduling behaviour related definitions. **********************************/
/******************************************************************************/

#define configTICK_RATE_HZ                         ( 1000U )
#define configUSE_PREEMPTION                       1
#define configUSE_TIME_SLICING                     1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION    0
#define configUSE_TICKLESS_IDLE                    1
#define configMAX_PRIORITIES                       5U
#define configMINIMAL_STACK_SIZE                   128U
#define configMAX_TASK_NAME_LEN                    4U
#define configTICK_TYPE_WIDTH_IN_BITS              TICK_TYPE_WIDTH_32_BITS
#define configIDLE_SHOULD_YIELD                    1
#define configTASK_NOTIFICATION_ARRAY_ENTRIES      1U
#define configQUEUE_REGISTRY_SIZE                  0U
#define configENABLE_BACKWARD_COMPATIBILITY        1
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS    0
#define configSTACK_DEPTH_TYPE                     size_t
#define configMESSAGE_BUFFER_LENGTH_TYPE           size_t
#define configUSE_NEWLIB_REENTRANT                 0

#define configENABLE_MPU                           0
#define configCHECK_HANDLER_INSTALLATION           0
/******************************************************************************/
/* Software timer related definitions. ****************************************/
/******************************************************************************/

#define configUSE_TIMERS                1
#define configTIMER_TASK_PRIORITY       ( configMAX_PRIORITIES - 1U )
#define configTIMER_TASK_STACK_DEPTH    configMINIMAL_STACK_SIZE
#define configTIMER_QUEUE_LENGTH        10U

/******************************************************************************/
/* Memory allocation related definitions. *************************************/
/******************************************************************************/

#define configSUPPORT_STATIC_ALLOCATION              1
#define configSUPPORT_DYNAMIC_ALLOCATION             1
#define configTOTAL_HEAP_SIZE                        4*4096U
#define configAPPLICATION_ALLOCATED_HEAP             0
#define configSTACK_ALLOCATION_FROM_SEPARATE_HEAP    0
#define configUSE_MINI_LIST_ITEM                     0

/******************************************************************************/
/* Interrupt nesting behaviour configuration. *********************************/
/******************************************************************************/

#define configKERNEL_INTERRUPT_PRIORITY          0U
#define configMAX_SYSCALL_INTERRUPT_PRIORITY     0U
#define configMAX_API_CALL_INTERRUPT_PRIORITY    0U

/******************************************************************************/
/* Hook and callback function related definitions. ****************************/
/******************************************************************************/

#define configUSE_IDLE_HOOK                   0
#define configUSE_TICK_HOOK                   0
#define configUSE_MALLOC_FAILED_HOOK          0
#define configUSE_DAEMON_TASK_STARTUP_HOOK    0
#define configCHECK_FOR_STACK_OVERFLOW        0

/******************************************************************************/
/* Run time and task stats gathering related definitions. *********************/
/******************************************************************************/

#define configGENERATE_RUN_TIME_STATS           0
#define configUSE_TRACE_FACILITY                0
#define configUSE_STATS_FORMATTING_FUNCTIONS    0
#define configKERNEL_PROVIDED_STATIC_MEMORY     1

/******************************************************************************/
/* Definitions that include or exclude functionality. *************************/
/******************************************************************************/

#define configUSE_TASK_NOTIFICATIONS           1
#define configUSE_MUTEXES                      1
#define configUSE_RECURSIVE_MUTEXES            1
#define configUSE_COUNTING_SEMAPHORES          1
#define configUSE_QUEUE_SETS                   1
#define configUSE_APPLICATION_TASK_TAG         1
#define INCLUDE_vTaskPrioritySet               1
#define INCLUDE_uxTaskPriorityGet              1
#define INCLUDE_vTaskDelete                    1
#define INCLUDE_vTaskSuspend                   1
#define INCLUDE_vTaskDelayUntil                1
#define INCLUDE_vTaskDelay                     1
#define INCLUDE_xTaskGetSchedulerState         1
#define INCLUDE_xTaskGetCurrentTaskHandle      1
#define INCLUDE_uxTaskGetStackHighWaterMark    1
#define INCLUDE_xTaskGetIdleTaskHandle         1
#define INCLUDE_eTaskGetState                  1
#define INCLUDE_xTimerPendFunctionCall         1
#define INCLUDE_xTaskAbortDelay                1
#define INCLUDE_xTaskGetHandle                 1
#define INCLUDE_xTaskResumeFromISR             1

#endif /* FREERTOS_CONFIG_H */
"""

        if not os.path.isdir(src_dir):
            os.makedirs(src_dir)
        with open(main_path, mode="w", encoding="utf8") as fp:
            fp.write(main_content.strip())
        with open(freertos_config_path, mode="w", encoding="utf8") as fp:
            fp.write(freertos_config_content.strip())

        return True


    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        board_config = self.board_config(board)
        build_core = variables.get(
            "board_build.core", board_config.get("build.core", "arduino"))
        build_mcu = variables.get("board_build.mcu", board_config.get("build.mcu", ""))

        frameworks = variables.get("pioframework", [])

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if board:
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("blackmagic", "jlink", "stlink", "cmsis-dap"):
            if link not in upload_protocols or link in debug["tools"]:
                continue
            if link == "blackmagic":
                debug["tools"]["blackmagic"] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug["tools"][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if IS_WINDOWS else
                                       "JLinkGDBServer")
                    }
                }
            else:
                server_args = ["-s", "$PACKAGE_DIR/openocd/scripts"]
                if debug.get("openocd_board"):
                    server_args.extend([
                        "-f", "board/%s.cfg" % debug.get("openocd_board")
                    ])
                else:
                    assert debug.get("openocd_target"), (
                        "Missed target configuration for %s" % board.id)
                    server_args.extend([
                        "-f", "interface/%s.cfg" % link,
                        "-c", "transport select %s" % (
                            "hla_swd" if link == "stlink" else "swd"),
                        "-f", "target/%s.cfg" % debug.get("openocd_target")
                    ])
                    server_args.extend(debug.get("openocd_extra_args", []))

                debug["tools"][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    }
                }
            debug["tools"][link]["onboard"] = link in debug.get("onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get("default_tools", [])

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "openocd" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-c", "adapter speed %s" % debug_config.speed]
                )
            elif "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )
