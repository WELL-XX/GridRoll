# 全新 E73 首次烧录与恢复

全新模块没有 USB 启动程序；直接拖入 UF2 无法首次安装。左右使用相同 `GridRoll-first-flash.hex`，然后分别安装左右应用。

## 首次包内容

`GridRoll-first-flash.hex` 包含 Adafruit nRF52 Bootloader 0.11.0 的 GridRoll 板定义、S140 6.1.1 和匹配 MBR、启动地址及 REGOUT0=3.3V 初始化记录。旁边的 `licenses/` 和第三方声明应与文件一起保存。

| 区域 | 地址 |
|---|---|
| MBR／S140 保留 | `0x00000–0x25FFF` |
| ZMK 应用 | `0x26000–0xEBFFF` |
| NVS 设置 | `0xEC000–0xF3FFF` |
| 启动程序／配置／MBR 参数／DFU 设置保留 | `0xF4000–0xFFFFF` |
| UICR 启动地址 | `0x10001014`，值 `0x000F4000` |
| UICR REGOUT0 | `0x10001304`，值 `0x00000005`（3.3V） |

首次包不包含键盘应用。地址检查同时核验实际 HEX／UF2 内容，禁止写入设置区或越过应用边界。不要将首次 HEX 当普通应用通过 UF2 拖入。

## 用 SWD 安装（J-Link／nrfjprog 示例）

给目标板正常供电，连接 SWDIO、SWCLK、GND、VTref；VTref 按实际 MCU 输出感测。以下步骤对**全新模块**执行，擦除会清空已有固件和设置：

```sh
nrfjprog --ids
nrfjprog -f NRF52 --eraseall
nrfjprog -f NRF52 --program GridRoll-first-flash.hex --verify
nrfjprog -f NRF52 --memrd 0x10001014 --n 4
nrfjprog -f NRF52 --memrd 0x10001304 --n 4
nrfjprog -f NRF52 --reset
```

存在多个探针时，给每条命令加 `--snr 实际探针序列号`。如果保护导致无法擦除，使用 `nrfjprog -f NRF52 --recover` 后重新安装；recover 会清空芯片数据。也可使用支持 nRF52840 的 SWD 工具加载完整 HEX，但必须保留 UICR 记录并执行校验。

读回启动地址应为 `000F4000`，REGOUT0 应为 `00000005`。断电后重新上电，实测 NRF_VDDR／轨迹球电源。编程成功但供电异常时先排查电源，不继续传感器功能验收。

## 通过 USB 安装左右应用

首次包安装后，无有效应用时启动程序应枚举为 **GRIDROLL** 磁盘。使用能传数据的 USB 线：

- 左侧拖入 `GridRoll-left.uf2`。
- 右侧拖入 `GridRoll-right.uf2`。

复制完成后磁盘会退出并启动应用。左右同时供电，先验证右侧 USB 按键，再验证左侧分体连接。右侧为电脑连接主机，左侧无需与电脑蓝牙配对。

## 再次进入启动程序

正常应用：同时按住 Fn 与 Mouse 进入 System，按目标侧底行最外侧的启动程序键。该行为按键来源在所在半边执行，左侧通过分体请求进入自己的启动程序。右侧有 USB Studio，可先修改键位再进入。

应用损坏或布局使启动键不可达：若 PCB 引出 RESET，可在约 500ms 内连按两次 RESET 进入 UF2。仅断电重上电不等于 double reset。没有可用 RESET 时，用 SWD 探针复位／重刷恢复；本版没有假定专用 DFU 按钮或状态 LED。

## 清除设置与重新配对

把 `GridRoll-settings-reset.uf2` 分别刷到两侧，给固件数秒完成擦除，再重新进入启动程序并刷回各侧正常 UF2。清除固件会持续用于清除设置，不应当正常键盘使用。它会清除 Studio／DYA 配置及蓝牙关系。

两侧均清除后，同时上电靠近放置，等待分体自动配对。电脑原有 GridRoll 蓝牙设备应先“忽略／删除”再重新配对。仅使用 System 层的 BT_CLR 只清除右侧当前主机槽的绑定，不等同于两侧分体设置重置。

## 故障恢复

- 没有 GRIDROLL 磁盘：检查数据线、VBUS／USB 接线、完整首次 HEX、UICR 启动地址与 3.3V 输出；必要时 SWD 重写。
- 右侧有键盘而左侧无输入：确认侧别文件、同时重置两侧设置后刷回，再检查左电源和矩阵。
- 轨迹球无输入而按键正常：先检查 3.3V、四根信号线和芯片型号；安装右侧诊断固件，通过 SWD 的 SEGGER RTT 读取探测日志。首次传感器 ID 应为 `0x30`。
- Studio 连不上：使用右侧正常／诊断应用、Chrome／Edge、USB 数据线，进入 System 按 Studio 解锁；关闭占用同一串口的其他页面。
