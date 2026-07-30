# 阶段 1：最小桌面窗口

阶段 1 提供可以实际运行的 PySide6 桌面宠物窗口基础：

- 透明背景
- 无系统边框
- 始终置顶
- 不在任务栏显示的工具窗口
- 按住鼠标左键拖动
- 拖动时限制在当前屏幕的可用区域
- 事件驱动的静态占位猫绘制，空闲时不运行持续计时器

## 运行

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m haqicat.app
```

关闭窗口可使用任务栏通知区域、任务管理器或终端中的
`Ctrl+C`。右键退出菜单将在后续阶段加入。

## 自动退出的原生冒烟测试

下面的命令会显示窗口、输出窗口属性，并在约 0.9 秒后退出：

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m haqicat.app --smoke-test
```

当前绘制内容仅用于验证窗口与交互，不是最终角色素材。

