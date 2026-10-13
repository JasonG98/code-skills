"""Render fictional reading-club examples, with no real project data."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'skills/flat-diagram-style/scripts'))
from flatkit import LIGHT, LINE, NAVY, SLATE, TEAL, TINT, WARN, Canvas

NOTICE = '虚构示例 · 所有名称、安排与数字仅用于演示图解样式'


def arch(output_dir):
    c = Canvas(1600, 1260, '社区读书会 · 组织与分工', NOTICE, 'arch')
    c.section(198, '按职责分组')
    groups = [
        ('参与人员', NAVY, ['读者', '主持人', '志愿者']),
        ('组织工作', TEAL, ['选择主题', '安排场地', '整理书单']),
        ('活动资源', SLATE, ['图书', '座椅', '讨论卡片']),
    ]
    y = 280
    for title, color, items in groups:
        c.rect(50, y, 1500, 140, LIGHT, 22)
        c.box(50, y, 260, 140, color, title)
        c.chips(345, y + 40, 1170, items, fill=TINT[color], h=60, size=26)
        y += 175
    c.section(840, '从想法到活动')
    c.chain(50, 930, 150, [
        (330, SLATE, '提出主题', '收集阅读兴趣'),
        (330, NAVY, '准备书单', '挑选讨论材料'),
        (330, NAVY, '组织交流', '分享各自观点'),
        (330, TEAL, '记录收获', '整理阅读笔记'),
    ], gap=60)
    c.strip(1150, '分组表示职责，箭头表示活动步骤的先后。', h=60)
    c.save(output_dir / 'gallery_arch.png', trim=False)


def charts(output_dir):
    c = Canvas(1600, 1450, '读书会报名 · 演示数据', NOTICE, 'charts')
    c.section(198, '示例汇总')
    c.kpi_row(280, 200, [('54', '合计报名人数（人）', NAVY),
                         ('3', '示例活动数（场）', TEAL),
                         ('18', '平均每场报名（人）', NAVY)], big=72)
    c.section(550, '每场报名人数（人）')
    values = [('活动 A', 24, NAVY), ('活动 B', 18, TEAL), ('活动 C', 12, SLATE)]
    c.hbars([(name, value, color, str(value), None) for name, value, color in values],
            640, label_w=230, scale=22, pitch=90)
    c.section(940, '同一组数据的柱形表示')
    base = 1250
    for x, (name, value, color) in zip([260, 700, 1140], values):
        c.vbar(x, base, 180, value, 9, color, str(value), name, size=36)
    c.line([(150, base), (1450, base)], LINE, 3)
    c.strip(1350, '两个视图使用同一组虚构数据；长度从零开始，按人数成比例绘制。', h=60, size=26)
    c.save(output_dir / 'gallery_charts.png', trim=False)


def sequence(output_dir):
    c = Canvas(1600, 1240, '活动准备 · 角色协作时序', NOTICE, 'sequence')
    xs = [250, 800, 1350]
    c.seq_participants([(xs[0], '参与者', SLATE), (xs[1], '主持人', NAVY),
                        (xs[2], '场地志愿者', TEAL)], y=240, w=360, bottom=1040)
    c.seq_msg(450, xs[0], xs[1], '报名活动')
    c.seq_self(560, xs[1], '整理名单')
    c.seq_msg(720, xs[1], xs[2], '确认场地安排')
    c.seq_msg(850, xs[2], xs[1], '回复准备情况', dash=True)
    c.seq_msg(980, xs[1], xs[0], '发送活动提醒')
    c.strip(1120, '从上到下表示先后顺序；实线表示发起沟通，虚线表示回复。', h=60, size=26)
    c.save(output_dir / 'gallery_sequence.png', trim=False)


def table(output_dir):
    c = Canvas(1600, 1030, '读书会形式 · 示例比较', NOTICE, 'table')
    rows = [
        ['圆桌讨论', '现场参与', '一张长桌', '自由发言与问答'],
        ['安静共读', '现场参与', '独立阅读座位', '阅读后简短分享'],
        ['线上交流', '远程参与', '线上会议空间', '轮流发言与文字留言'],
        ['主题分享', '现场或远程', '小型分享空间', '围绕同一主题交流'],
    ]
    c.table(50, 290, [260, 340, 360, 540], ['形式', '参与方式', '空间需求', '交流方式'],
            rows, rh=120, hh=90, fs=28, hs=30, bold_col=[0])
    c.strip(920, '各形式按相同维度展示；示例不预设推荐方案。', h=60, size=26)
    c.save(output_dir / 'gallery_table.png', trim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', type=Path)
    output_dir = parser.parse_args().output_dir
    WARN.clear()
    for render in (arch, charts, sequence, table):
        render(output_dir)
    print('warnings:', WARN)
    if WARN:
        raise SystemExit('Review layout warnings before publishing examples.')


if __name__ == '__main__':
    main()
