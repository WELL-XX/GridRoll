// SPDX-License-Identifier: MIT
#ifndef GRIDROLL_BOOT_BOARD_H
#define GRIDROLL_BOOT_BOARD_H
#define LEDS_NUMBER        0
#define NEOPIXELS_NUMBER   0
#define UICR_REGOUT0_VALUE UICR_REGOUT0_VOUT_3V3
// Deliberately use LDOs: external DC/DC inductors have not been confirmed.
#define ENABLE_DCDC_0       0
#define ENABLE_DCDC_1       0
#define BLEDIS_MANUFACTURER "PandaKB"
#define BLEDIS_MODEL        "GridRoll E73"
// pid.codes in-house test identity; replace before distribution/manufacturing.
#define USB_DESC_VID          0x1209
#define USB_DESC_UF2_PID      0x0001
#define USB_DESC_CDC_ONLY_PID 0x0002
#define UF2_PRODUCT_NAME      "GridRoll Bootloader"
#define UF2_VOLUME_LABEL      "GRIDROLL"
#define UF2_BOARD_ID          "nRF52840-GridRoll-E73-v1"
#define UF2_INDEX_URL         "https://github.com/WELL-XX/GridRoll"
#endif
