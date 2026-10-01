# SPDX-License-Identifier: MIT
zephyr_library()
zephyr_library_sources_ifdef(CONFIG_GRIDROLL_PAW3222 drivers/input/paw3222.c drivers/input/paw3222_sdio.c)
zephyr_library_sources_ifdef(CONFIG_NEWLIB_LIBC drivers/compat/newlib_fini.c)

# Pinned runtime-input/ZMK revisions use printf functions without stdio.h
# in several Studio sources. Supply declarations without editing fetched code.
if(CONFIG_ZMK_RUNTIME_INPUT_PROCESSOR_STUDIO_RPC)
  target_compile_options(app PRIVATE -include stdio.h)
endif()
