# HaqiCat

HaqiCat 是一个面向 Windows 的 Python 3 / PySide6 桌面宠物项目，形象方向参考《魔法少女的魔女审判》中二阶堂希罗相关的“哈气猫”。

当前仓库处于**阶段 0：工程初始化**。此阶段只建立可运行的工程骨架和环境检查工具，尚未实现桌面窗口与动画。

## 当前环境检查结果

检查日期：2026-07-30

| 组件 | 状态 | 备注 |
| --- | --- | --- |
| Git | 可用 | 2.53.0.windows.2 |
| Python 3 | 部分可用 | 系统未安装可供 `python`/`py` 使用的解释器；Codex 工作区内置 Python 3.12.13 可用 |
| PySide6 | 未安装 | 后续安装 |
| PyInstaller | 未安装 | 后续安装 |

> PySide6 和 PyInstaller 的安装会联网获取并落地可执行组件，因此需要得到用户确认后再进行。

## 阶段目标

第一阶段计划逐步完成：

- 透明无边框窗口
- 窗口始终置顶
- 鼠标拖动
- 待机动画
- 随机走动
- 屏幕边界限制
- 右键退出菜单
- 较低的 CPU 占用

每完成一个可运行阶段，都应实际运行验证并创建一次本地 Git commit。

## 工程结构

```text
HaqiCat/
├─ assets/
│  └─ character/
│     ├─ source/       # 从网络获取、尚未处理的角色素材
│     └─ processed/    # 清理、裁切和动画处理后的素材
├─ src/
│  └─ haqicat/         # 应用程序包
├─ tests/              # 自动化测试
├─ tools/              # 环境检查等开发工具
├─ pyproject.toml
└─ requirements.txt
```

## 本地准备

建议安装 Python 3.11 或 3.12，然后在项目目录执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

安装完成后检查环境：

```powershell
python tools\check_environment.py
```

运行当前工程骨架：

```powershell
$env:PYTHONPATH = "src"
python -m haqicat
```

## 素材说明

角色素材将在后续阶段从公开网页检索并保存到 `assets/character/source/`。使用前会记录来源、用途与可确认的授权信息；仓库默认不提交未经确认的原始素材。若公开素材的使用许可不明确，将只用于本地原型验证，发布版本需要替换为获得授权或自行制作的素材。

## 开发阶段

1. **阶段 0（当前）**：检查环境、创建工程骨架和文档。
2. **阶段 1**：安装依赖，创建透明、无边框、置顶且可拖动的最小窗口。
3. **阶段 2**：获取并处理角色素材，加入低频率待机动画。
4. **阶段 3**：加入随机走动、屏幕边界限制和右键退出菜单。
5. **阶段 4**：性能检查、PyInstaller 打包和 Windows 实机验证。

