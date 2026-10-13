"""Render the fictional style reference used by the portable skill bundle."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'skills/flat-diagram-style/scripts'))
from flatkit import NAVY, SLATE, TEAL, WARN, Canvas


def render_reference(output_dir):
    c = Canvas(1600, 1120, '社区读书会 · 从想法到活动',
               '虚构示例 · 所有名称与安排仅用于演示图解样式', 'reference')
    c.section(198, '活动准备流程')
    c.chain(50, 290, 180, [
        (330, SLATE, '确定主题', '收集阅读兴趣'),
        (330, NAVY, '选择书目', '准备讨论材料'),
        (330, NAVY, '安排活动', '确定时间与地点'),
        (330, TEAL, '分享收获', '留下阅读笔记'),
    ], gap=60)
    c.section(550, '阶段安排')
    c.box(50, 650, 690, 300, NAVY, '准备阶段',
          '收集参与意向\n整理讨论问题\n确认活动安排', ts=36, bs=30, gap=24)
    c.box(860, 650, 690, 300, TEAL, '活动当天',
          '介绍阅读主题\n轮流分享观点\n记录后续书单', ts=36, bs=30, gap=24)
    c.arrow([(752, 800), (848, 800)])
    c.label(800, 735, '开始活动', size=24)
    c.strip(1010, '样张展示：纯色圆角块、统一间距、清晰层级与简洁连线。', h=60, size=26)
    return c.save(output_dir / 'reference_replica.png', trim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    WARN.clear()
    print(render_reference(args.output_dir))
    print('warnings:', WARN)
    if WARN:
        raise SystemExit('Review layout warnings before publishing the reference.')


if __name__ == '__main__':
    main()
