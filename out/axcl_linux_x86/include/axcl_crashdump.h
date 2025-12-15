/**************************************************************************************************
 *
 * Copyright (c) 2019-2024 Axera Semiconductor Co., Ltd. All Rights Reserved.
 *
 * This source file is the property of Axera Semiconductor Co., Ltd. and
 * may not be copied or distributed in any isomorphic form without the prior
 * written consent of Axera Semiconductor Co., Ltd.
 *
 **************************************************************************************************/

#ifndef __AXCL_CRASHDUMP_H__
#define __AXCL_CRASHDUMP_H__

#include "axcl_base.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Crash dump configuration structure
 *
 * All fields are optional (can be nullptr). Configuration priority:
 * environment variables > interface config > defaults.
 * Dump file prefix is automatically detected from module name.
 */
typedef struct {
    const char* dump_dir;      // Dump file output directory
    const char* dump_type;     // Dump type/level (e.g., "Normal", "FullMemory")
} axclCrashDumpConfig;

/**
 * @brief Initialize crash dump functionality
 *
 * Registers a global exception filter that automatically generates .dmp files on crash.
 * Thread-safe, can be called multiple times (only first call takes effect).
 *
 * @param config Configuration structure pointer (nullptr to use environment variables)
 * @return true if initialization succeeded
 *
 * @example
 * axclCrashDumpConfig config = { .dump_dir = "C:\\dumps", .dump_type = "Normal" };
 * axclInitializeCrashDump(&config);
 */
AXCL_EXPORT bool axclInitializeCrashDump(const axclCrashDumpConfig* config);

/**
 * @brief Uninitialize crash dump functionality
 *
 * Optional call, mainly used for testing. Automatically cleaned up on program exit.
 */
AXCL_EXPORT void axclUninitializeCrashDump(void);

/**
 * @brief Dump type options
 *
 * Supported types:
 * - Normal: Basic information (stack, registers, module list). Small size (few MB).
 *   Recommended for most cases, sufficient for most debugging needs.
 * - FullMemory: Full memory dump. Large size (may be GB), use only when detailed memory analysis is needed.
 * - WithDataSegs: Include data segments. Medium size.
 * - WithHandleData: Include handle data. Medium size.
 * - WithIndirectMemory: Indirectly referenced memory. Medium size.
 *
 * Can be combined with comma (e.g., "Normal,WithDataSegs"). Default: Normal.
 *
 * Note: In most cases, "Normal" is sufficient and recommended.
 */

#ifdef __cplusplus
}
#endif

#endif /* __AXCL_CRASHDUMP_H__ */