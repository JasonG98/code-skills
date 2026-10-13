# 按关系选图型

这些是构图方法，不限定领域、语言或输出格式。代码适用于 [flatkit](toolkit.md)，假设已有 `c = Canvas(W, H, margin=margin)`；先根据目标画幅给出 `y`、高度和间距，再计算位置。示例文字不是真实业务事实，使用时替换。

| 要解释的关系 | 常用布局 | 保留的信息 |
|---|---|---|
| 顺序、操作步骤 | 横向链 / 纵向流程 | 先后、条件、分支 |
| 组成、层级、归属 | 分层 / 嵌套容器 / 树 | 边界、父子、各层职责 |
| 多个对象的异同 | 并列卡片 / 对照表 | 相同维度、相同单位 |
| 随时间推进 | 时间线 / 阶段图 | 时间或序号、阶段、里程碑 |
| 主体间消息 | 时序图 / 泳道 | 参与者、方向、时序 |
| 数值大小 | 条形 / 柱形 / 指标卡 | 基线、比例、单位、时间口径 |
| 多对多关联 | 节点连接图 | 连接含义；复杂图可用已有自动布局工具 |

## 流程、分支和回路

```python
from flatkit import NAVY

gap, node_h = 60, 150
steps = [("输入", "已有材料"), ("处理", "操作说明"), ("输出", "交付内容")]
node_w = (c.content_w - gap * (len(steps) - 1)) / len(steps)
pos = c.chain(c.margin, y, node_h,
              [(node_w, NAVY, title, body) for title, body in steps], gap=gap)
bottom = y + node_h
```

窄幅改成纵向：逐个 `box()`，连接上一块底部与下一块顶部。分支先布置各目标节点，再从实际源节点边缘连线；给条件写标签。回路在主链外预留走线空间，连接真实端点，不按示例抄固定坐标。

## 分层与分组

```python
from flatkit import LIGHT, NAVY, TINT

row_h, gap, label_w = 150, 40, c.content_w * 0.25
layers = [("服务对象", ["成员", "访客"]), ("活动内容", ["讨论", "练习"])]
for title, items in layers:
    c.rect(c.margin, y, c.content_w, row_h, LIGHT, 20)
    c.box(c.margin, y, label_w, row_h, NAVY, title)
    tags_bottom = c.chips(c.margin + label_w + 30, y + 40,
                          c.content_w - label_w - 60, items, fill=TINT[NAVY])
    y = max(y + row_h, tags_bottom) + gap
```

标签超过容器高度时扩大容器后重画，或把该层单独展开。空间上的上下排列不自动代表数据流；确有调用或依赖时才加箭头。

## 对比与表格

先选共享维度，再给每个对象填写对应内容。未提供优劣依据时各对象同等突出；有明确推荐结论才突出推荐项。不要默认“新方案更好”。

```python
rows = [["方案 A", "线上", "异步参与"], ["方案 B", "现场", "集中讨论"]]
colw = [c.content_w * ratio for ratio in (0.25, 0.3, 0.45)]
bottom = c.table(c.margin, y, colw, ["方案", "形式", "参与方式"], rows)
```

长文本可用等宽卡片；同时提高高度并显式断行，不靠持续减小字号容纳。

## 时间线与时序

时间线用 `line()` 连接里程碑，`circle()` 标记事件，标签在两侧交错排列。等距步骤图表示顺序，不表示等长时间；若距离编码时长，应按真实日期计算。

时序图根据参与者数量和画布宽度计算中心点：

```python
from flatkit import NAVY

names = ["申请人", "服务台", "处理人"]
lane_w = c.content_w / len(names)
xs = [c.margin + lane_w * (i + 0.5) for i in range(len(names))]
c.seq_participants([(x, name, NAVY) for x, name in zip(xs, names)],
                   y=y, w=lane_w * 0.7, bottom=c.H - c.margin)
c.seq_msg(y + 180, xs[0], xs[1], "提交申请")
c.seq_msg(y + 280, xs[1], xs[2], "转交材料")
```

参与者较多时扩宽、分段或使用自动布局，不设置统一的“最多五个”。消息线之间的空间应容纳实际标签与自调用，生命线应覆盖全部消息。

## 少量指标和数值

`kpi_row()` 用于已知数字及其说明，数字不能替代来源与口径。要比较长度时，从零开始，用同一比例换算；先给分类名与数值标签留空间，再用剩余长度除以最大值。全部为零时直接显示零，不除以零。

`hbars()` / `vbar()` 仅用于简单非负值。负值、对数轴、误差区间、时间序列和密集数据用完整图表工具。不同指标的“改善倍数”必须先确认计算方法和好坏方向，不统一写“越长越好”。

## 空间取舍

通常先保留关系和正文可读性，再减少装饰和冗余文字。拆图依据是读者能否在目标尺寸读清，而非固定小节数量。大图分解时，各图共享颜色含义、字号层级和图例；不要为了视觉一致而更改数据尺度。
