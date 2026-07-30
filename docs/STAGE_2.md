# 阶段 2：哈气猫精灵与低频待机动画

阶段 2 将用户提供的哈气猫参考图转化为独立制作的透明桌宠精灵，
并接入低频率状态动画。

## 精灵

`assets/character/processed/` 包含：

- `haqi_cat_idle.png`
- `haqi_cat_hiss.png`
- `haqi_cat_sleep.png`
- `haqi_cat_walk_left.png`
- `haqi_cat_walk_right.png`

所有精灵均为 256×256 RGBA PNG，生成时使用用户提供的四张图片作为
视觉参考，再通过纯色键控去除背景。图片生成采用内置图像生成模式，
最终文件经过本地透明边缘检查。

## 当前行为

- 待机状态以 700 毫秒间隔做轻微呼吸变化
- 每隔约 8 至 16 秒随机哈气一次
- 右键菜单可以手动哈气、趴下休息、恢复待机或退出
- 趴睡时停止待机和随机行为计时器
- 鼠标左键拖动与屏幕边界限制继续有效

当前没有高帧率循环或忙等待，空闲 CPU 开销应保持较低。

## 运行

双击：

```text
run_haqicat.cmd
```

自动退出的原生窗口验证：

```powershell
.\run_haqicat.cmd --smoke-test
```

