// SPDX-License-Identifier: MIT
/* Arm GNU 14's Newlib pulls in __libc_fini_array through its exit path.
 * Zephyr owns startup and never tears down this C-only application.
 * A weak hook also permits a toolchain-provided implementation to take priority. */
__attribute__((weak)) void _fini(void) {}
