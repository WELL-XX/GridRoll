# GridRoll

PandaKB GridRoll 的原创分体 ZMK 固件：E73 nRF52840、47 键、左侧 EC11、右侧 PAW3222 轨迹球和 DYA Studio。

右侧固定为 Central，负责 USB／蓝牙输出、轨迹球与 Studio；左侧固定为 Peripheral，通过蓝牙连接右侧。USB 默认优先，整机深睡和轨迹球惯性默认关闭。两侧采用内部低频 RC 时钟。

## 开始使用

1. 在本私有仓库的 **Actions → Build GridRoll firmware** 中打开成功的构建。
2. 下载 `GridRoll-first-flash` 和 `GridRoll-firmware` 两个产物。
3. 全新 E73 必须先按 [首次烧录说明](docs/first-flash.md) 用 SWD 写入启动程序；随后通过 USB 拖入对应侧的 UF2。
4. 按 [维护说明](docs/maintenance.md) 配对、修改键位和调整轨迹球。

每次提交、拉取请求或手动运行都会编译。产物保留 30 天，过期后可以重新运行构建。源码、日志和产物均受私有仓库访问权限控制；不启用 GitHub Pages，也不公开发布 Release。

## 文件分工

| 目录／文件 | 用途 |
|---|---|
| `config/gridroll.keymap` | 全部默认键位、层、旋钮行为与轨迹球输入处理 |
| `config/gridroll*.conf` | 通用设置及左右角色设置 |
| `config/west.yml` | 固定版本的 ZMK、Zephyr 和 DYA 模块依赖 |
| `boards/pandakb/gridroll_e73/` | E73 板、USB、内部 RC 时钟和 Flash 分区 |
| `boards/shields/gridroll/` | 严格按硬件排列的矩阵、旋钮、轨迹球与 47 键物理布局 |
| `drivers/input/paw3222_sdio.*` | 可独立测试的 GPIO 半双工总线 |
| `drivers/input/paw3222.c` | 传感器初始化、MOTION 中断和本地输入事件 |
| `bootloader/gridroll/` | 无猜测 LED／DFU 按钮的专用 UF2 启动程序板定义 |
| `scripts/`、`tests/`、`ci/` | 构建、地址检查、硬件约束测试和固定工具版本 |
| `docs/` | 接线、烧录、恢复、维护及实物验收 |

## 默认层

Base 为 QWERTY。底行全局列 4 按住进入 Fn，列 7 按住进入 Mouse；同时按住两键进入 System。

- Fn：F1–F12、数字、符号及导航。
- Mouse：W/A/S/D 位置移动鼠标，H/J/K 位置为左／中／右键，U/M 位置上下滚动；轨迹球 XY 变为滚动。
- System：顶行依次为 Studio 解锁、蓝牙槽 0–4、USB、BLE、输出切换、两透明键、清除当前主机蓝牙绑定。底行最左／最右为所在侧启动程序，紧邻内侧为所在侧重启。
- Extra 1–4：预留 Studio 编辑层，首次启用时为透明键。

左侧旋钮默认顺时针增加音量、逆时针减小音量、按压静音；Mouse 层旋转滚动，按压为中键。旋钮按压仅对应 `RC(3,3)`，不额外生成第二个按键。初始 `steps=20` 与 `triggers-per-rotation=20`，实际每圈事件数见维护说明。

**源码默认键位与 Studio 保存键位是两份数据。** 普通 UF2 更新保留键盘中的 Studio／DYA 设置。只改源码再更新固件，不一定覆盖已保存键位；恢复方法见维护说明。

## 构建与验证

Actions 同时提供左右 UF2／HEX、右侧 RTT 诊断 UF2／HEX、设置清除 UF2／HEX和首次烧录 HEX。应用范围为 `0x26000–0xEBFFF`，设置为 `0xEC000–0xF3FFF`，启动程序保留 `0xF4000–0xFFFFF`。

固定依赖版本与已知兼容处理见 [开发维护](docs/maintenance.md)，软件和实物结果见 [验证记录](docs/validation.md)。编译成功不代表硬件已验收。

## 上游与许可

原始实现使用 MIT 许可；依赖保留各自许可，见 [第三方声明](THIRD_PARTY_NOTICES.md)。启动程序的 USB `1209:0001/0002` 仅限内部测试，对外产品必须换成正式分配的标识。普通应用使用 ZMK 的共享 USB 标识。
