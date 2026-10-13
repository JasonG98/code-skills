# PNG 工具：flatkit

仅在选择 Pillow 绘制静态 PNG 时阅读。本工具使用逻辑像素坐标和 2× 超采样；不是自动布局引擎，不提供 SVG、PPT 原生对象或统计图表系统。

## 运行与字体

需要 Python 3 和 Pillow。先复用现有可用环境；如果使用 uv，可在任务目录执行 `uv run --with pillow draw.py`。不要为一张图改动无关项目依赖或自动安装系统字体。

先定位本技能目录，以其 `scripts/` 导入模块，避免依赖当前工作目录。下面例子把目录作为命令行参数传入，不假设具体安装位置。

字体按需查找 macOS、Linux、Windows 的常用系统和用户字体目录，优先寻找 CJK 字体，再找常见西文字体。找到字体不代表它覆盖所有字符。中文、其他语言、数学符号、emoji 和从右到左文字须查看实际渲染；复杂文字排版不满足要求时使用支持该语言的工具。

指定字体：

```python
from flatkit import configure_fonts
configure_fonts(regular="/path/to/regular.ttf", bold="/path/to/bold.ttf")
# TTC/OTC 集合可指定 index；未指定则优先选择简体中文和相应字重。
# configure_fonts(regular="/path/to/font.ttc", index=0)
# configure_fonts() 恢复自动发现。
```

这是进程级配置，改变字体时会清除文字缓存。只提供 regular 时其他字重使用同一文件，不能保证有真正粗体。工具不自动下载字体，也不检查逐字的字形覆盖。

## 最小可运行示例

保存为任务目录的 `draw.py`，执行 `uv run --with pillow draw.py /actual/path/to/flat-diagram-style ./outputs/flow.png`。

```python
from pathlib import Path
import sys

skill_dir = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(skill_dir / "scripts"))
from flatkit import Canvas, WARN

width, height, margin, gap = 1200, 675, 60, 60
c = Canvas(width, height, name="registration", margin=margin)
labels = ["Register", "Confirm", "Attend"]
node_w = (c.content_w - gap * (len(labels) - 1)) / len(labels)
WARN.clear()
c.chain(margin, 240, 180,
        [(node_w, "#6941A5", label, None) for label in labels], gap=gap)
c.save(Path(sys.argv[2]), trim=False)
print("Layout warnings:", WARN)
```

这个示例没有标题和强调条。要改变语言，替换文字并选择合适字体；要改变长宽比，重新计算布局。改变画布宽度不会自动缩放字号、节点、间距或已有坐标。

## 布局与配色

- `Canvas(W, H, title='', subtitle=None, name='', *, background=WHITE, margin=50)` 接受任意合适的整数宽高，背景为不透明颜色。`content_w = W - 2 * margin`。
- 内置标题位置仍适合较大画布：标题 y=60、字号 50；副标题 y=142、字号 31。小图或自定义版式可省略它们，再用 `raw()` / `stack()` 排版。
- `strip()` 和 `kpi_row()` 的默认宽度随画布和边距变化。其他组件由调用方给坐标与尺寸；修改背景不会自动重配所有组件颜色。
- `box()` 支持自定义颜色，自动在深色和白色文字中选择对比更高的一种；`color=` 可显式覆盖。透明背景或复杂主题优先用更合适的渲染方案。
- `stack()` 和 `box()` 只识别显式 `\n` 换行，放不下时缩字。缩到 0.78× 以下会记录到全局 `WARN`。遇到告警，先加宽、断行、精简或换版式；`WARN` 为空也不能证明没有溢出。
- `raw()` 不检测文字越界；`chips()` 会换行但不会拆开一个过长标签；布局调用应自行计算底部位置和边界。
- `save(path, trim=True, margin=None)` 默认裁掉底部空白。固定尺寸、幻灯片比例、对齐的一组图使用 `trim=False`；裁剪不能恢复已经画出画布的内容。

## API 索引

| API | 用途 / 注意点 |
|---|---|
| `section(y, text, x=None, accent=AMBER, size=36, color=None)` | 小节标题；`accent=None` 去掉竖条；也可完全省略小节 |
| `box(x,y,w,h,fill,title,body,ts=32,bs=26,...)` | 圆角块；`items=[T(...)]` 定制多行文本 |
| `chain(x,y,h,specs,gap=64,...)` | 水平链；spec 为 `(w,fill,title,body[,box_kwargs])`；返回各块位置 |
| `line(points,...)` / `arrow(points,...)` | 折线 / 箭头；箭头末段须非零长；短间距需减小箭头头部 |
| `label(cx,cy,text,...)` | 连线标签，默认白底；自定义背景时设置 `bg=` |
| `pill(...)` / `chips(...)` | 标签 / 可换行标签组 |
| `strip(y,text,...)` / `kpi_row(y,h,cards,...)` | 整行提示 / 非空指标卡组 |
| `hbars(rows,y,...)` / `vbar(...)` | 简单非负数值条形，不含完整坐标轴；统计分析优先图表工具 |
| `table(x,y,colw,header,rows,...)` | 表格；列宽之和由可用宽度决定 |
| `seq_participants(...)` / `seq_msg(...)` / `seq_self(...)` / `seq_cross(...)` | 时序图组件；参与者位置、生命线长度和消息间距由调用方决定 |
| `trap(...)` / `rect(...)` / `poly(...)` / `circle(...)` | 基础图形 |
| `T(text,size=28,w='Regular',color=None)` / `stack(...)` / `raw(...)` | 文本样式 / 块内排版 / 直接绘字 |
| `placeholder(x,y,w,h,text,...)` | 有意预留的信息位置，不要求每个缺失数据都画一个框 |

完整参数见 [flatkit.py](../scripts/flatkit.py)；按关系选布局见 [配方](recipes.md)。脚本可复现 PNG，但不能代替用户要求的可编辑矢量文件。
