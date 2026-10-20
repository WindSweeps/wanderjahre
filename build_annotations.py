"""Build the reading companion from individually verified reference notes."""
from pathlib import Path
import json
import re

P = Path(__file__).parent
sources = json.loads((P / 'sources.json').read_text())
notes = []
for name in ['annotations-H.json', 'annotations-R-extra.json', 'annotations-A.json', 'annotations-C.json']:
    notes.extend(json.loads((P / name).read_text()))
by_id = {x['id']: x for x in notes}
assert len(notes) == len(by_id) == len(sources) == 57
assert set(by_id) == {x['id'] for x in sources}

short_titles = {
 'H1':'维也纳手工业条例校勘本', 'H2':'欧洲手工业：迁移与技术传播论文集',
 'H3':'维也纳帮工条例研究', 'H6':'Güntzer旅行自述', 'H7':'Güntzer行程与语料范围',
 'H8':'Hans Sachs与工匠文化', 'H9':'Platter自传资料库', 'H10':'Platter学术传记',
 'H11':'帮工行会的形成', 'H12':'当代Walz民族志', 'H13':'1436年条例的档案线索',
 'H14':'上莱茵的工匠流动', 'H15':'工艺秘密与技术转移', 'H16':'Otto Baur与知识转移争论',
 'R1':'城乡行会与流动网络', 'R2':'18世纪荷兰帮工的迁移与定居',
 'R3':'前现代熟练劳动的流通', 'R4':'工匠、家仆与迁移控制', 'R5':'流动人口的排斥',
 'R6':'丢勒文字遗产：家庭纪事', 'R7':'帮工组织与熟练劳动市场',
 'A1':'丢勒的艺术与职业环境', 'A2':'丢勒旅行展的传统叙事', 'A3':'《圣杰罗姆》的技术与归属',
 'A4':'Luber的威尼斯研究', 'A5':'Stewart对Luber的书评', 'A6':'早期丢勒与传记循环论证',
 'A7':'《早期丢勒》展览图录', 'A8':'巴塞尔的荷尔拜因', 'A9':'荷尔拜因的跨境职业生涯',
 'A10':'女性、性别与行会史学', 'A11':'帮工的男性气质', 'A12':'身份污名与职业排除',
 'A13':'当代Walz非遗说明', 'A14':'制度形式与功能的变化', 'A15':'丢勒的旧版学术传记',
 'A16':'早期印刷与巴塞尔网络', 'A17':'丢勒家庭纪事抄本',
 'C1':'Epstein：训练与技术变迁', 'C2':'Ogilvie：行会效率解释的反驳',
 'C3':'Ogilvie：行会经济学综述', 'C4':'行会与创新论文集导论',
 'C5':'行业准入与移民大师', 'C6':'Ogilvie：包容与攫取为何并存',
 'C7':'欧洲学徒制比较', 'C8':'法国compagnonnage历史',
 'C9':'普罗旺斯compagnonnage早期踪迹', 'C10':'法国compagnonnage的非遗表述',
 'C11':'英格兰学徒训练的机制', 'C12':'英格兰学徒制的长期变化',
 'C14':'威尼斯行会、技术与经济', 'C15':'威尼斯学徒、工作与社会',
 'C16':'Grand Tour与阶层化旅行', 'C17':'中国会馆、公所与行会概念',
 'C18':'日本的座与株仲间', 'C19':'compagnon不等于兄弟会成员',
 'C20':'南陆奥木匠的技术积累'
}

intro = '''# Wanderjahre参考资料逐条导读

**57条资料的大意、重要观点、原文短摘与中文译解**

对应[原调研正文](wanderjahre.md)的全部参考编号；原有编号存在跳号，沿用以免破坏引用。核读与整理日期：2026年10月7日。

## 如何使用这份导读

每条资料依次列出实际阅读范围、内容大意、重要观点、原文短摘及译文，并补充一条与Wanderjahre有关的“为什么”。“追问与用途”是本次调研的分析，不是原作者的话；译文为本次译解。原文保留来源语言和原有拼写，截取片段时注明；页码使用印刷页码，必要时另列PDF页序。

这57条包含研究论文、专著、史料编订本、书评、博物馆与档案资料，证据性质各不相同。能够读到全文的，也只按下文注明的实际核读部分概括，不将局部精读冒充全书通读。原文采用短摘，较长上下文可沿来源链接阅读。

**需要特别区分的条目：** H11、A11尚未取得可可靠核读的实质正文，其“观点”栏只列可确认信息与待核问题，原文仅为编目或题名；A4只读公开前置页和简介，短摘为章节题名；A7依据馆方图录介绍；A17依据抄本编目，相关家庭纪事文本另见R6的1920年编订本。A5引用的是书评作者Stewart的判断，不能署为Luber原话。

## 建议的并读路径

| 想解决的问题 | 优先并读 | 比较时要抓住什么 |
| --- | --- | --- |
| 游历究竟是求知，还是劳动力管理？ | [H1](#ref-H1)、[H15](#ref-H15)、[H16](#ref-H16)、[R2](#ref-R2) | 区分制度目的、个人动机和实际结果。 |
| 行会促进创新，还是保护既得利益？ | [C1](#ref-C1)、[C2](#ref-C2)、[C5](#ref-C5)、[C6](#ref-C6) | 比较解释机制、统计分母及被排除的人。 |
| 艺术家的旅行传记可靠吗？ | [R6](#ref-R6)、[A4](#ref-A4)、[A5](#ref-A5)、[A6](#ref-A6)、[A3](#ref-A3) | 区分自述、作品归属、技术检测与后世推断。 |
| 谁可以体面地流动？ | [R4](#ref-R4)、[R5](#ref-R5)、[A10](#ref-A10)、[A12](#ref-A12) | 对比信用证明、性别、出身与救济资格。 |
| 为什么不同地区有不同的训练与迁移组合？ | [C7](#ref-C7)、[C8](#ref-C8)、[C11](#ref-C11)、[C14](#ref-C14)、[C17](#ref-C17)、[C18](#ref-C18) | 先比较规则、资金、庇护和就业渠道，再比较组织名称。 |
| 我们遗漏了哪些流动和劳动者？ | [R7](#ref-R7)、[H7](#ref-H7)、[C19](#ref-C19)、[C20](#ref-C20) | 检查临时居留、资料截取、身份称谓和保存偏差。 |

## 全部条目索引

'''
groups = [('H', '制度史与史料'), ('R', '补充研究与迁移机制'), ('A', '艺术、身份与当代制度'), ('C', '时空比较与史学论争')]
out = [intro]
for prefix, label in groups:
    items = [s for s in sources if s['id'].startswith(prefix)]
    out.append(f'**{prefix} · {label}（{len(items)}条）**\n\n')
    for s in items:
        sid = s['id']
        out.append(f'- [{sid} {short_titles[sid]}](#ref-{sid})\n')
    out.append('\n')

for prefix, label in groups:
    out.append(f'## {prefix} · {label}\n\n')
    for s in [s for s in sources if s['id'].startswith(prefix)]:
        sid = s['id']
        a = by_id[sid]
        qurl = a.get('quote_url') or a.get('source_url') or s['url']
        q = a['quote'].strip()
        assert q and len(q.split()) <= 25, (sid, len(q.split()))
        out.append(f'<a id="ref-{sid}"></a>\n\n### {sid} · {short_titles[sid]}\n\n')
        out.append(f"**{s['author']}（{s['year']}）**，[{s['title']}]({s['url']})。\n\n")
        if s.get('locator'):
            out.append(f"**书目信息：** {s['locator']}\n\n")
        out.append(f"**实际阅读范围：** {a['read_scope']}\n\n")
        out.append(f"**大意：** {a['summary']}\n\n")
        heading = '可确认的信息与待核问题' if sid in ['H11', 'A11', 'A17'] else '重要观点'
        out.append(f'**{heading}：**\n\n')
        for point in a['points']:
            out.append(f'- {point}\n')
        out.append(f"\n**原文短摘｜{a['quote_kind']}：**\n\n> {q}\n\n")
        out.append(f"**中文译解：** {a['translation']}\n\n")
        out.append(f"**出处与定位：** {a['locator']} [查看原文来源]({qurl})。\n\n")
        out.append(f"**追问与用途：** {a['use']}\n\n**证据边界：** {a['limits']}\n\n")
        extras = []
        seen_urls = {s['url'], qurl}
        for label, url in s.get('extra', []) + a.get('extra_urls', []):
            if url not in seen_urls:
                extras.append((label, url))
                seen_urls.add(url)
        if extras:
            out.append('**其他入口：** ' + '；'.join(f'[{label}]({url})' for label, url in extras) + '。\n\n')
        out.append(f'[回到原调研中的{sid}](wanderjahre.md#ref-{sid})\n\n---\n\n')

md = ''.join(out)
assert len(re.findall(r'^### [HRAC]\d+ ·', md, re.M)) == 57
assert len(re.findall(r'^> ', md, re.M)) == 57
assert not re.search(r'|turn\d+(?:view|search)', md)
anchors = set(re.findall(r'<a id="([^"]+)"', md))
targets = set(re.findall(r'\]\(#([^)]+)\)', md))
assert targets <= anchors
dest = P / 'wanderjahre-annotated-bibliography.md'
dest.write_text(md)
report = {
    'entries': len(sources), 'quotes': 57,
    'characters': len(md), 'bytes': len(md.encode()),
    'external_urls': len(set(re.findall(r'\]\((https?://[^)]+)\)', md))),
    'quote_word_counts': {a['id']: len(a['quote'].split()) for a in notes},
    'unresolved_substantive_body': ['H11', 'A11'],
    'catalogue_or_contents_quotes': ['H11', 'A4', 'A11', 'A17'],
}
(P / 'annotations-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'quote_word_counts'}, ensure_ascii=False))

# The website shares the same records; the Markdown output remains unchanged.
from reader_template import build_site
site_bytes = build_site(sources, notes, short_titles, groups, intro)
print(json.dumps({'website':str(P / 'index.html'), 'bytes':site_bytes}, ensure_ascii=False))
