# HaqiCat

HaqiCat 是一个使用 Python 3 与 PySide6 开发的 Windows 桌面宠物，形象方向参考
《魔法少女的魔女审判》中二阶堂希罗相关的“哈气猫”。

当前版本已具备透明无边框、始终置顶、屏幕边界限制、鼠标拖动、右键退出、
低频率连续动画，以及基础点击互动。

## 启动

双击项目根目录中的 `HaqiCat.vbs`。它会使用项目虚拟环境中的 `pythonw.exe`
启动桌宠，不会一直显示黑色命令窗口，也不会修改系统设置。

`run_haqicat.cmd` 仅用于开发和排错，需要查看诊断输出时再使用。

## 当前互动

- 待机：呼吸、上下浮动、轻微摇摆与随机自然眨眼
- 单击：哈气并抖动
- 双击：趴下休息；再次双击恢复待机
- 左键拖动：切换为被从背后拎起的动作；松手后下坠、回弹并晃头
- 右键：哈气、休息/恢复或退出
- 空闲时：贴地爬行一小段或哈气；爬完先收拢四肢并保持低趴观察，再撑起身体回到待机
- 屏幕边缘：保持在工作区域内，并在爬到边缘时转身

## 环境准备

推荐 Python 3.11 或 3.12。项目当前使用 Python 3.12、PySide6 和 PyInstaller。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

开发模式运行：

```powershell
$env:PYTHONPATH = "src"
python -m haqicat
```

运行测试：

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## 工程结构

```text
HaqiCat/
├─ assets/character/processed/  # 已处理的透明角色素材
├─ docs/                        # 每个可运行阶段的记录
├─ src/haqicat/                 # 桌宠程序
├─ tests/                       # 自动测试
├─ tools/                       # 环境检查和素材处理工具
├─ HaqiCat.vbs                  # 推荐的无黑框启动入口
└─ run_haqicat.cmd              # 开发诊断入口
```

## 迭代路线

- 已完成：基础窗口、素材状态、拖动与边界限制、右键菜单
- 已完成：无黑框启动、连续待机动作、点击哈气、双击休息
- 已完成：拎起拖动、落地缓冲、随机走动、停步观察和边缘转向
- 已完成：参考真实猫低姿态步态制作的左右四相爬行循环
- 已完成：爬行收势与低趴观察过渡
- 已完成：低趴观察结束后的撑起与半跪起身过渡
- 已完成：无全身抖动的随机三相眨眼
- 后续：继续细化肩胛与后爪节奏、制作哈气多帧素材，以及 PyInstaller 窗口程序打包

项目按可运行的小阶段迭代；每一阶段都会实际运行验证、提交 Git，并在更新前
保留可回退的远端备份分支。
