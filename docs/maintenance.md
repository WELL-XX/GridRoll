# 调整、Studio 与开发维护

## 键位

`config/gridroll.keymap` 是源码默认值。每层都按全局行优先排列：前三行各 12 键，底行 11 键，省略列 8 的空位。底行旋钮按压只占全局列 3。修改默认键位后提交即可触发 Actions。

键盘已在 Studio 保存键位时，正常 UF2 更新会继续使用保存值。优先在 Studio 中修改并保存；要重新采用源码默认值，使用 Studio 提供的恢复默认操作，或按首次烧录说明把设置清除 UF2 刷到两侧再刷回正常固件。清除操作也会清空蓝牙／DYA 设置。

四个预留层可在 Studio 中启用并编辑。更改层号、删层或重排层时，应同步检查 Fn+Mouse→System 的条件层和 Mouse 轨迹球覆盖层；这些设备树规则仍按编译时层号引用，不能假设所有外部引用都会随 Studio 重排自动更新。

## DYA Studio 与轨迹球

用桌面 Chrome／Edge 打开 [DYA Studio](https://studio.dya.cormoran.works/)，右侧通过 USB 连接，选择 GridRoll 串口。Fn+Mouse→System，按顶行第一个键解锁。网页的权限选择由用户在浏览器确认。

固件提供 `mouse` 和 `scroll` 两个 runtime input processor，并启用 custom-settings RPC。Base／Fn 使用 mouse；Mouse 层覆盖为 scroll，默认把 XY 转为水平／垂直滚动，倍率 1/60。可以调整速度倍率、X/Y 反向、旋转和 XY 转滚动；硬件 CPI 默认 988，可在右侧 overlay 的 `res-cpi` 修改，范围 608–4826、步进 38。

运行时设置有 RAM 与 Flash 两种模式。临时调参可选 Memory only；确定后 **Save All** 保存，断电后应保持。**Discard All** 重新载入已保存值，**Reset All** 恢复固件中的处理器默认值并保存。没有相应按钮或接口时，可打开上游 [Runtime input processor 页面](https://cormoran.github.io/zmk-module-runtime-input-processor/) 直接通过 USB 调整；避免两个页面同时占用串口。

上游 DYA 页面可能展示其他型号的功能。本版提供键位编辑和两个处理器的运行时调参；没有定义电池采样、原始传感器图像、传感器硬件 CPI RPC 或额外硬件，不应把这些项目当成已经支持。

惯性和自动鼠标层默认关闭。需要开启时，单独记录参数和断电／重连后的实测结果。首次验收先保持默认设置，以便区分供电、接线和输入处理问题。

## 旋钮校准

左侧 `gridroll.dtsi` 的 `steps` 描述驱动每圈原始步数，`triggers-per-rotation` 描述每圈期望行为事件数；两者初始为 20。先缓慢转一整圈再快速转一整圈，记录各自事件数，目标 16–40，无反向／漏报／重复。

实际编码器的脉冲与卡点规格可能不同；按测得原始步数调整 steps，再调整事件数。不要只凭 EC11 名称判断。方向反了可交换 A/B 配置或该层 sensor-bindings 的顺序，避免改动已经确认的 PCB 接线。按压以矩阵 `RC(3,3)` 测一次，不另加 GPIO 按压行为。

## 蓝牙与输出

右侧与电脑配对，左侧仅与右侧连接。System 顶行槽 0–4 选择主机，BT_CLR 清除当前主机绑定；USB／BLE／输出切换键用于选择首选输出，选择会保存。清空设置后的默认值为 USB 优先，可在没有 USB 时回退到蓝牙。

分体重连失败时，先确认两侧文件和电源，再同时清除两侧设置；主机也删除旧的 GridRoll 配对。不要只清一侧后长期混用旧绑定。

## 诊断

`GridRoll-right-diagnostics.uf2` 保留正常功能和 Studio，通过 SEGGER RTT 输出传感器日志。接 SWD 探针，用 RTT 客户端查看启动 ID、初始化 CPI 及总线错误；日志不与 Studio USB 串口混用。无传感器／探测失败时仅停止轨迹球，键盘与分体应继续工作。

GPIO 总线采用 mode 3、MSB 优先，默认半周期 5µs、读转向等待 100µs、事务间隔 50µs，均可在右侧传感器节点中调整。读取前 SDIO 转为输入；所有 GPIO 失败路径均尝试 CS 释放、SCLK 恢复高、SDIO 释放。初始化最多 3 次尝试；运行错误最多 3 次快速重试，随后降至 1Hz，避免持续占用工作队列。

实际波形、模式／时序余量和轨迹球方向须在实物验证。诊断固件也没有改为上游的共享 MOSI/MISO SPI 实现。

## 固定依赖与兼容处理

`config/west.yml` 固定 ZMK custom-studio 分支、Zephyr 4.1 修复版和两个 DYA 模块的完整提交 SHA，传递依赖由这些固定 manifest 决定；Actions 还保存 `west-frozen.yml`。Python 工具锁定于 `ci/requirements.lock`。固件构建镜像固定 digest；启动程序固定 Adafruit 0.11.0 SHA、Git 子模块 SHA 和 Arm GNU 12.3.rel1 下载 SHA256。

右侧使用完整 Newlib 数学库、GNU 静态初始化及较大的输入／RPC 线程栈；本地模块为所固定的上游 Studio C 源码补充 stdio 声明，不编辑下载依赖。升级时应重新确认这项兼容处理是否仍需要。

升级时一次只改一组依赖，检查完整 Actions、47 键、Studio 解锁／保存、DYA 参数保存、分体重连和供电。不要把 revision 改成 main 来绕过失败。

## 本地构建

需要 Zephyr 4.1 兼容 SDK、Python 3.12+、CMake、Ninja、Git。仓库本身是模块，应把依赖工作区放在仓库外：

```sh
python3 -m venv ../gridroll-tools
. ../gridroll-tools/bin/activate
pip install -r ci/requirements.lock
mkdir -p ../gridroll-workspace/config
cp config/west.yml ../gridroll-workspace/config/west.yml
west init -l ../gridroll-workspace/config
cd ../gridroll-workspace
west update --narrow --fetch-opt=--filter=blob:none
cd ../GridRoll
python scripts/check_hardware.py
cc -Wall -Wextra -Werror -std=c11 -Idrivers/input tests/test_sdio.c drivers/input/paw3222_sdio.c -o /tmp/gridroll-test-sdio
/tmp/gridroll-test-sdio
python scripts/build_firmware.py --workspace ../gridroll-workspace --out artifacts
```

使用官方 Arm GNU 代替 Zephyr SDK 时，设 `ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb` 和 `GNUARMEMB_TOOLCHAIN_PATH=实际工具链目录`，不要用缺少 libc 能力声明的 cross-compile 模式构建 DYA。

启动程序：按 `bootloader/upstream.json` 克隆并检出固定 SHA，初始化子模块；执行 `python scripts/build_bootloader.py --source 启动程序目录 --out artifacts`。脚本会验证 SHA、安装 GridRoll 板定义，并构建两种上游基准板。

## 产品化前

将启动程序 USB 标识改成正式分配值，重新构建并做 UF2／SWD 恢复测试。电池分压和 ADC 接线确认后，再独立加入电池测量和 P0.05 控制；不要凭模块常见电路套用。真实验收记录保存在 validation 文档中。
