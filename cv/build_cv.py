# -*- coding: utf-8 -*-
"""从 index.html 生成学术简历 PDF 源文件（精简版 / 完整版 × 中 / 英）"""
import re, json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'cv')
os.makedirs(OUT, exist_ok=True)

H = open(SITE, encoding='utf-8').read()
Z2E = json.load(open(os.path.join(ROOT, '_zh2en.json'), encoding='utf-8'))


def strip_tags(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip()


def norm(x):
    x = x.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    return re.sub(r'\s+', ' ', x).strip()


def en_of(zh):
    return Z2E.get(zh) or Z2E.get(norm(zh)) or ''


# ---------------- 解析全量清单 ----------------
def section(a, b):
    s = H.index('<section id="%s"' % a)
    e = H.index('<section id="%s"' % b) if b else len(H)
    return H[s:e]


def parse_groups(sec_html):
    """返回 [(组名, [(key, date, title, grade, work)])]"""
    parts = sec_html.split('<div class="grp reveal')
    groups = []
    for p in parts[1:]:
        name = re.search(r'<span class="zh">(.*?)</span>', p)
        if not name:
            continue
        items = []
        for m in re.finditer(r'data-d="(\w+)">\s*(?:<span class="y">([^<]*)</span>)?<h4>(.*?)</h4>', p, re.S):
            raw = m.group(3)
            g = re.search(r'<b>(.*?)</b>', raw)
            w = re.search(r'<em>(.*?)</em>', raw)
            t = strip_tags(re.sub(r'<b>.*?</b>|<em>.*?</em>', '', raw))
            items.append((m.group(1), (m.group(2) or '').strip(), t.strip(' ·'),
                          strip_tags(g.group(1)) if g else '', strip_tags(w.group(1)) if w else ''))
        groups.append((name.group(1), items))
    return groups


AWARD_GROUPS = parse_groups(section('award', 'train'))
TRAIN_GROUPS = parse_groups(section('train', 'skill'))

MISSING = []


def en_line(item):
    """把 (date,title,grade,work) 拼成英文一行；缺译文则回落中文并记录"""
    _, date, title, grade, work = item
    parts = []
    t = en_of(title)
    if not t:
        MISSING.append('TITLE: ' + title)
        t = title
    parts.append(t)
    if grade:
        g = en_of(grade)
        if not g:
            MISSING.append('GRADE: ' + grade)
            g = ''
        if g:
            parts.append(g)
    if work:
        w = en_of(work)
        if not w:
            MISSING.append('WORK: ' + work)
            w = ''
        if w:
            parts.append(w)
    return date, ' — '.join(parts[:2]) + (' · ' + parts[2] if len(parts) > 2 else '')


# ---------------- 内容：精简版 ----------------
def P(date, title, sub=None, items=None, fo=False):
    """fo=True → 仅完整版显示，精简版隐藏"""
    return dict(date=date, title=title, sub=sub, items=items or [], fo=fo)


def compact(lang):
    zh = lang == 'zh'
    if zh:
        return [
            ('研究概述', None, [
                P('', '美术史与物质文化研究者 · 人类学田野工作者'),
            ], [
                '以学术研究为主业，兴趣集中于人类学、物质文化与图像学。历史学训练让我从一手材料与现场提问，美术史训练让我读图、断代与辨伪，人类学视角则把器物、图像与仪式放回具体的人群与日常去理解。',
                '研究沿三条线索展开：澳门墓葬建筑图像与中西视觉交融、粤西与黔东的非遗田野与口述史、景德镇手工艺群体的生产与身份。已形成期刊论文 2 篇、硕士学位论文 1 篇、国际学术会议口头报告 5 次。',
            ], [
                '<b>研究兴趣：</b>物质文化与手工艺 · 墓葬建筑与图像学 · 非遗田野与口述史 · 文化遗产数字化保护 · 区域国别与跨文化交流',
            ]),
            ('教育经历', None, [
                P('2022 — 2024', '澳门科技大学 · 美术学硕士（美术史研究）',
                  '人文艺术学院。毕业论文《澳门墓葬建筑图像研究》——以建筑民族志、文献研究法与图像志／图像学方法，对澳门现存 17 座坟场的墓碑建筑作结构、形制与图像的全面考察；论文收录于校图书馆学位论文库。', None),
                P('2024 — 2026', '景德镇陶瓷大学 · 雕塑',
                  '美术学院，全日制统招两年（第二学士学位），平均成绩 85.2，GPA 3.52 / 4。', None),
                P('2018 — 2022', '广东石油化工学院 · 历史学学士',
                  '文法学院。毕业论文《浅谈日本社会主义失败的原因》；曾获一等奖学金、三好学生、优秀毕业生。', None),
            ], None, None),
            ('论文与发表', '2 篇期刊论文（均独立作者）· 1 篇硕士学位论文 · 5 次国际学术会议口头报告', [
                P('', '<b>期刊论文</b>'),
                P('2024', '《广东张田饼印田野调查——兼论张田饼印图像民俗学解读》',
                  '《民艺》2024 年第 1 期（ISSN 2096-5257）——以图像民俗学方法解读饼印雕刻中的民俗文化底蕴。<i>个人代表作</i>'),
                P('2021', '《茂名市革命遗址“寻访”记》',
                  '《炎黄地理》2021 年第 6 期，页 98–100（ISSN 2095-6185）——配合茂名市革命遗址普查撰写。'),
                P('', '<b>学位论文</b>'),
                P('2024', '《澳门墓葬建筑图像研究》',
                  '澳门科技大学硕士学位论文（英文题名 A Study on the Architectural Images of Tombstones in Macao），2024 年 6 月通过答辩。'),
                P('', '<b>会议论文与口头报告</b>'),
                P('2026.09', '《澳门墓葬场存的历史演变及其文明互鉴启示》',
                  '区域国别学·北京论坛 2026（北京第二外国语学院区域国别学院），分论坛论文宣讲。'),
                P('2026.08', 'The Forgotten Emotional Geography: Emotion, Memory and Cross-Cultural Empathy in the Cemeteries and Tombstone Architecture of Modern Macao',
                  '第三届全球南方研究国际学术研讨会（越南胡志明市国家人文社科大学 USSH-VNUHCM），口头报告；摘要评审均分 3.83 / 5。'),
                P('2026.05', 'Space and Culture: A Study on the Historical Evolution of Cemeteries and Tombstone Architecture in Modern Macao',
                  'International Migration & Intercultural Communication 跨学科学生大会（英国爱丁堡大学历史、古典与考古学院），口头报告（15 分钟），收录待发于《sine》。'),
                P('2026.04', '同上题（岭南大学场）',
                  '香港岭南大学研究院 Postgraduate Conference 2026，口头报告（香港）。'),
                P('2025.08', '《仪式实践中的共生秩序与认同调适：以贵州印江土家族村落信俗田野调查为例》',
                  '“铸牢中华民族共同体意识与乡村振兴”研讨会（贵阳·手上记忆博物馆），口头报告（稿件编号 KSK-2025-011）。'),
            ], None, None),
            ('研究项目', None, [
                P('2024', '南风窗“调研中国”——景德镇陶瓷手工艺从业者研究 · 团队成员',
                  '《为生产完整的人：后农业模式下景德镇陶瓷手工艺从业者研究》入围全国十强并获三等奖、优秀调研记录奖；承担调研框架设计、访谈、实地调研、视频拍摄剪辑与报告撰写全流程。'),
                P('2022 — 2023', '广东省非遗张田饼印田野调查 · 负责人',
                  '对非遗传承人进行访谈与过程记录，对饼印图案作图像学分析；调查报告获第三届“记录乡土中国”优秀奖，成果发表于《民艺》2024 年第 1 期。'),
                P('2020 — 2021', '广东省茂名市革命遗址普查 · 负责人',
                  '配合茂名市政府党史地志办完成市区革命遗址系统普查：测量记录遗址现状、口述史采集与整理、撰写田野调查报告；获大学生创新创业项目校级与省级立项。'),
            ], None, None),
            ('田野与实践', None, [
                P('2024.12 — 2025.01', '贵州《村寨志》编撰（印江中尧村）· 编撰成员',
                  '参与土家族传统村寨田野调查与村寨志编写，从口述、碑刻、图文等多渠道发掘村落历史与民俗，为村落文化建档。'),
                P('2024.08 — 2024.10', '玉门市博物馆艺术驻留（甘肃）· 驻留艺术家',
                  '参与“昌马世瑞”二期项目：对昌马石窟第 2、4 窟壁画作复原性临摹（扫描采集—走线—填色—泥板做旧），协助整理约 140 ㎡ 壁画资料并参与遗产活化，成果无偿捐赠玉门市博物馆。'),
                P('2022.05 — 2022.07', '茂名市政府党史地志办 · 实习生',
                  '参与革命遗址田野调查与革命后代口述访谈，整理地方史资料；负责翻译近代侵华日军书信日文文献（日语 N1）。', None, True),
            ], None, None),
            ('获奖 · 学术与研究', None, [
                P('2026.05', '第七届“光祈杯”全国高校艺术学科学生论文比赛 · 本科生组 三等奖 —— 论文《澳门墓碑建筑图像研究》'),
                P('2026.05', '第五届“记录乡土中国”暨 2026 寒假大学生民俗文化社会调查 二等奖 —— 《非马之马：纸马仪式中的马文化重构——基于云南多民族的田野调查报告》'),
                P('2025.11', '第三十七届韩素音国际翻译大赛 · 日译汉 优秀奖'),
                P('2025.04', '第四届“记录乡土中国”暨 2025 寒假大学生民俗文化社会调查 二等奖 —— 贵州铜仁印江土家族村落信仰信俗田野调查'),
                P('2024.01', '第三届“记录乡土中国”大学生民俗文化社会调查 优秀奖 —— 《张田饼印田野调查报告》（河南省口头与非物质文化遗产中心）'),
                P('2022.03', '第十七届“挑战杯”全国大学生课外学术科技作品竞赛 国赛二等奖'),
                P('2021.07', '第十六届“挑战杯”广东大学生课外学术科技作品竞赛 省一等奖'),
                P('2026.02', '作品《骏骨凝香》入选“骏马呈祥”第九届江西省生肖雕塑大展　〔创作〕'),
            ], None, None),
            ('研修 · 方法与国际课程', None, [
                P('2026.07', '国家艺术基金 2026《寿州窑创新技艺人才培训》人才培训班'),
                P('2026.07', 'QualiTaTi 暑期学校 · AI for Qualitative Research（成绩 A · 90.33/100）'),
                P('2026.06', '第六届全国大学生人类学训练营（浙江大学人类学研究所）〔另：2025.06 第五届〕'),
                P('2026.04', '北京大学 · 城乡建成环境文化遗产理论与方法：流域文明研究生暑期学校'),
                P('2026.03', '杜伦大学、牛津大学等联合课程《濒危考古：利用遥感技术保护文化遗产》'),
            ], None, None),
            ('语言 · 方法 · 其他能力', None, [
                '<b>语言：</b>日语 JLPT N1（2019）· 大学日语六级 CJT-6（2026）· 大学日语四级（2024）；英语 CET-4（511）；普通话二级乙等（83.4）；粤语、客家话（母语）；拉丁语、苏美尔语、阿卡德语（课程训练）',
                '<b>方法与工具：</b>田野调查与口述史、图像学与图像志、AI 辅助质性研究（NVivo 编码）、大数据与因果推断基础、SAS Visual Analytics、遥感考古与三维建模（C4D / ZBrush / 三维扫描）、陶瓷考古修复与金缮',
                ('S', '<b>创作与认证（辅）：</b>陶瓷雕塑作品入选第九届江西省生肖雕塑大展、获“中超利永杯”青年陶艺家技能大赛新锐奖，《海韵黎纹紫金陶瓦猫》被海南紫金陶艺术馆收藏；另持高级中学教师资格（日语）、陶瓷工艺品制作师、评茶师（高级）等认证。'),
                ('F', '<b>创作实践（辅）：</b>2023 年起在浙江龙泉设立个人陶瓷工作室并常驻创作；《骏骨凝香》入选第九届江西省生肖雕塑大展与内蒙古首届陶瓷艺术作品展，《沃土生花》获“中超利永杯”青年陶艺家技能大赛新锐奖，《春日来信》获“绘就绿色未来”主题艺术作品比赛优秀奖，《海韵黎纹紫金陶瓦猫》被海南紫金陶艺术馆收藏。田野中积累的形体、纹样与节奏，反哺这些偶尔为之的创作。'),
                ('F', '<b>其他认证：</b>高级中学教师资格（日语）· 陶瓷工艺品制作师（成型师·五级）· 评茶师（高级工·三级）· 红十字救护员 + CPR & AED · 中国登山协会一级山地户外运动'),
            ], [], None, None),
        ]
    # ---------------- 英文 ----------------
    return [
        ('Research Profile', None, [
            P('', 'Art Historian & Material-Culture Researcher · Anthropological Fieldworker'),
        ], [
            'Research is my main line, with interests concentrated in anthropology, material culture and iconography: history taught me to question through primary sources and the site itself, art history to read images and date them, anthropology to put objects and ritual back among the people who make them. Three threads run through my work — funerary architectural imagery and Sino-Western visual hybridity in Macao; intangible heritage, fieldwork and oral history in western Guangdong and eastern Guizhou; and the production and identity of the Jingdezhen handicraft community. To date: two journal articles, one master’s thesis, five international conference presentations.',
        ], [
            '<b>Research interests:</b> Material Culture & Handicraft · Funerary Architecture & Iconography · Intangible Heritage, Fieldwork & Oral History · Digital Safeguarding of Cultural Heritage · Area Studies & Cross-Cultural Exchange',
        ]),
        ('Education', None, [
            P('2022 — 2024', 'Macau University of Science and Technology · Master of Fine Arts, History of Fine Arts',
              'Faculty of Humanities and Arts. Thesis: <i>A Study of Macao Funerary Architectural Imagery</i> — architectural ethnography, documentary research, iconography and iconology applied to a full survey of structure, form and imagery across the 17 cemeteries extant in Macao; held in the MUST Library thesis repository.'),
            P('2024 — 2026', 'Jingdezhen Ceramic University · Sculpture',
              'Academy of Fine Arts; two-year full-time programme (second bachelor’s degree), average 85.2, GPA 3.52 / 4.'),
            P('2018 — 2022', 'Guangdong University of Petrochemical Technology · BA, History',
              'School of Humanities and Law. Thesis: <i>On the Causes of the Failure of Japanese Socialism</i>. First-class scholarship; outstanding graduate.'),
        ], None, None),
        ('Publications', '2 journal articles (sole author) · 1 master’s thesis · 5 international conference presentations', [
            P('', '<b>Journal articles</b>'),
            P('2024', 'Fieldwork on the Zhangtian Cake Moulds of Guangdong: with a Discussion of Their Imagery from the Perspective of Folkloric Iconography',
              'MinYi (Folk Arts) 2024(1), ISSN 2096-5257 — fieldwork and iconographic analysis of the meanings carved into cake moulds. <i>Representative work.</i>'),
            P('2021', 'In Search of the Revolutionary Sites of Maoming',
              'Yanhuang Geography 2021(6), pp. 98–100, ISSN 2095-6185 — written alongside the Maoming revolutionary-site survey.'),
            P('', '<b>Master’s thesis</b>'),
            P('2024', 'A Study of Macao Funerary Architectural Imagery',
              'MUST master’s thesis (English title: A Study on the Architectural Images of Tombstones in Macao); defended June 2024.'),
            P('', '<b>Conference papers and oral presentations</b>'),
            P('2026.09', 'The Historical Evolution of Macao’s Burial Grounds and Its Lessons for Mutual Learning among Civilisations',
              'Area Studies · Beijing Forum 2026 (Beijing International Studies University), panel presentation.'),
            P('2026.08', 'The Forgotten Emotional Geography: Emotion, Memory and Cross-Cultural Empathy in the Cemeteries and Tombstone Architecture of Modern Macao',
              '3rd International Symposium on Global South Studies (USSH-VNUHCM, Vietnam); abstract review 3.83/5.'),
            P('2026.05', 'Space and Culture: A Study on the Historical Evolution of Cemeteries and Tombstone Architecture in Modern Macao',
              'International migration and intercultural communication student congress, University of Edinburgh; 15-minute paper; forthcoming in <i>sine</i>.'),
            P('2026.04', 'Same paper · Lingnan University session',
              'Postgraduate Conference 2026, Lingnan University (Hong Kong): oral presentation of the same paper.'),
            P('2025.08', 'Symbiotic Order and Identity Adjustment in Ritual Practice: Fieldwork on Village Beliefs among the Tujia of Yinjiang, Guizhou',
              'Symposium on intangible heritage and rural development, Guiyang; paper no. KSK-2025-011.'),
        ], None, None),
        ('Research Projects', None, [
            P('2024', '“Investigating China” (Southern Weekly/Nanfengchuang) — Jingdezhen Ceramic Handicraft Practitioners · Research team member',
              'Producing the Complete Person: Jingdezhen ceramic handicraft practitioners — national top ten, Third Prize and Best Fieldwork Record Award; responsible for research design, interviews, survey, filming and report writing.'),
            P('2022 — 2023', 'Fieldwork on Guangdong Intangible Heritage: the Zhangtian Cake Moulds · Principal investigator',
              'Interviews with inheritors and process documentation; iconographic analysis of mould patterns; report won the 3rd “Recording Rural China” Excellence Award; results in MinYi 2024(1).'),
            P('2020 — 2021', 'Survey of Revolutionary Sites in Maoming, Guangdong · Principal investigator',
              'Systematic survey of revolutionary sites in urban Maoming with the municipal Party-history office: measuring and recording present conditions, collecting oral histories, writing fieldwork reports; funded as university and provincial innovation projects.'),
        ], None, None),
        ('Fieldwork & Practice', None, [
            P('2024.12 — 2025.01', 'Village Gazetteer of Zhongyao Village, Yinjiang, Guizhou · Editorial member',
              'Fieldwork and gazetteer writing on a Tujia village; its history and folkways documented through oral accounts, stelae and images.'),
            P('2024.08 — 2024.10', 'Artist Residency, Yumen City Museum, Gansu · Artist in residence',
              '“Changma Shirui” phase II: restorative copying of murals in Caves 2 and 4 of the Changma Grottoes; documentation of c. 140 m² of mural material; results donated to the museum.'),
            P('2022.05 — 2022.07', 'Party History and Local Gazetteer Office, Maoming Municipal Government · Intern',
              'Field survey of revolutionary sites and interviews with descendants of revolutionaries; collation of local historical materials; translation of wartime Japanese correspondence.', None, True),
        ], None, None),
        ('Awards · Academic & Research', None, [
            P('2026.05', '7th “Guangqi Cup” National Student Paper Competition in Art Disciplines · Third Prize, undergraduate division — paper: A Study of Macao Funerary Architectural Imagery'),
            P('2026.05', '5th “Recording Rural China” University Student Folk-Culture Social Survey · Second Prize — Not-a-Horse: the Reconstruction of Horse Culture in Paper-Horse Ritual, based on fieldwork among several ethnic groups in Yunnan'),
            P('2025.11', '37th Han Suyin International Translation Competition · Excellence Award, Japanese–Chinese'),
            P('2025.04', '4th “Recording Rural China” University Student Folk-Culture Social Survey · Second Prize — fieldwork on village beliefs among the Tujia of Yinjiang, Tongren, Guizhou'),
            P('2024.01', '3rd “Recording Rural China” University Student Folk-Culture Social Survey · Excellence Award — Zhangtian Cake Mould fieldwork report (Henan Centre for Oral and Intangible Cultural Heritage)'),
            P('2022.03', '17th “Challenge Cup” National Undergraduate Extracurricular Academic Science & Technology Works Competition · National Second Prize'),
            P('2021.07', '16th “Challenge Cup” Guangdong Undergraduate Academic Science & Technology Works Competition · Provincial First Prize'),
            P('2026.02', 'Fragrance of Steed Bones selected for the 9th Jiangxi Provincial Zodiac Sculpture Exhibition [creative work]'),
        ], None, None),
        ('Programmes · Method & International Courses', None, [
            P('2026.07', 'China National Arts Fund 2026 — Innovative Craft Talent Training Programme, Shouzhou Kiln'),
            P('2026.07', 'QualiTaTi Summer School · AI for Qualitative Research (grade A · 90.33/100)'),
            P('2026.06', '6th National Undergraduate Anthropology Training Camp, Zhejiang University (also the 5th, 2025.06)'),
            P('2026.04', 'Peking University graduate summer school: Theory and Method of Built-Environment Cultural Heritage — River-Civilisation'),
            P('2026.03', 'Durham, Oxford et al. · Endangered Archaeology: Protecting Cultural Heritage with Remote Sensing'),
        ], None, None),
        ('Languages · Methods · Other Competence', None, [
            '<b>Languages:</b> Japanese JLPT N1 (2019), CJT-6 (2026), College Japanese Test Band 4 (2024); English CET-4 (511); Putonghua Level 2-B (83.4); Cantonese and Hakka (mother tongues); Latin, Sumerian and Akkadian (coursework)',
            '<b>Methods and tools:</b> Fieldwork and oral history; iconography and iconology; AI-assisted qualitative research (NVivo coding); foundations of big-data analysis and causal inference; SAS Visual Analytics; remote-sensing archaeology and 3D modelling (C4D, ZBrush, structured-light scanning); archaeological ceramic restoration and kintsugi',
            ('S', '<b>Creative practice & certification (secondary):</b> Ceramic sculpture selected for the 9th Jiangxi Provincial Zodiac Sculpture Exhibition and awarded at the “Chaojiao Liyong Cup” young ceramists competition; Tile Cat collected by the Hainan Zijin Ceramic Art Museum. Also holds senior-high-school teacher qualification (Japanese), Ceramic Craft Maker and Tea Taster certification.'),
            ('F', '<b>Creative practice (secondary):</b> Since 2023 I have kept a ceramic studio in Longquan, Zhejiang — Fragrance of Steed Bones selected for the 9th Jiangxi Provincial Zodiac Sculpture Exhibition and the 1st Inner Mongolia Ceramic Art Exhibition; Blossoming Earth awarded at the “Chaojiao Liyong Cup” young ceramists competition; Letter from Spring awarded at the “Painting a Green Future” art competition; Tile Cat collected by the Hainan Zijin Ceramic Art Museum.'),
            ('F', '<b>Other certification:</b> Senior-high-school teacher qualification (Japanese); Ceramic Craft Maker (L5); Tea Taster (L3); Red Cross first-aid + CPR & AED; CMA Grade-1 Mountain Outdoor Sports'),
        ], [], None, None),
    ]


HEADER = {
    'zh': dict(name='嵇 鸿 轩', latin='JI HONGXUAN (Hongxuan Ji)',
               role='美术史与物质文化研究者 · 人类学田野工作者　〔副线：陶瓷雕塑创作〕',
               contact=['+86 133 0234 0686', 'kekogen@foxmail.com', '现居：江西景德镇', '1999 年生']),
    'en': dict(name='HONGXUAN JI', latin='Ji Hongxuan · 嵇鸿轩',
               role='Art Historian & Material-Culture Researcher · Anthropological Fieldworker (secondary line: ceramic sculpture)',
               contact=['+86 133 0234 0686', 'kekogen@foxmail.com', 'Based in Jingdezhen, Jiangxi', 'b. 1999']),
}

TITLES = {
    'zh': dict(note_short='学术简历 · 精简版', note_full='学术简历 · 完整版（含全部获奖与研修清单）'),
    'en': dict(note_short='Curriculum Vitae · Short Form', note_full='Curriculum Vitae · Full (with complete award and programme lists)'),
}


def render(lang, variant):
    full = variant == 'full'
    hd = HEADER[lang]
    secs = compact(lang)
    ehun = {}
    parts = []
    parts.append('<div class="hd"><div class="hd-l">')
    parts.append('<div class="nm">%s <span class="lt">%s</span></div>' % (html.escape(hd['name']), html.escape(hd['latin'])))
    parts.append('<div class="role">%s</div>' % html.escape(hd['role']))
    parts.append('<div class="contact">%s</div>' % '　·　'.join(html.escape(x) for x in hd['contact']))
    parts.append('</div><img class="photo" src="../assets/id_photo.jpg" alt=""></div>')

    def block(title, note, rows, paras, chips, cols=False):
        o = ['<div class="sec">']
        o.append('<h2>%s</h2>' % html.escape(title))
        if note:
            o.append('<div class="note">%s</div>' % note)
        for p in paras or []:
            o.append('<p class="tag">%s</p>' % p)
        for c in chips or []:
            o.append('<p class="tag">%s</p>' % c)
        if cols:
            o.append('<div class="cols">')
        for r in rows:
            if not full and r.get('fo'):
                continue
            o.append('<div class="entry"><div class="main">')
            o.append('<div class="t">%s</div>' % r['title'])
            if r['sub']:
                o.append('<div class="sub">%s</div>' % r['sub'])
            for it in r['items']:
                o.append('<li>%s</li>' % it)
            o.append('</div><div class="when">%s</div></div>' % html.escape(r['date']))
        if cols:
            o.append('</div>')
        o.append('</div>')
        return '\n'.join(o)

    # 前 5 节（研究概述…田野与实践）原样输出
    for title, note, rows, paras, chips in secs[:5]:
        parts.append(block(title, note, rows, paras, chips))

    if full:
        # 获奖：完整清单（三组）
        grp_en = {'学术 · 研究': 'Academic & Research', '文学 · 翻译': 'Literature & Translation',
                  '艺术 · 展览 · 设计': 'Art, Exhibitions & Design'}
        for gname, items in AWARD_GROUPS:
            rows = []
            for it in items:
                _, date, title, grade, work = it
                if lang == 'zh':
                    line = strip_tags(title)
                    if grade:
                        line += ' · ' + grade
                    if work:
                        line += ' —— ' + work
                    rows.append(P(date, html.escape(line)))
                else:
                    d, line = en_line(it)
                    rows.append(P(d, html.escape(line)))
            parts.append(block(
                ('获奖' if lang == 'zh' else 'Awards') + ' · ' +
                (gname if lang == 'zh' else grp_en.get(gname, gname)),
                None, rows, None, None, True))
        # 研修：完整清单
        tr_en = {'田野 · 人类学 · 研究方法': 'Fieldwork · Anthropology · Methods',
                 '语言 · 古典学 · 文学': 'Languages · Classics · Literature',
                 '国际课程 · 认证': 'International Programs & Certificates',
                 '文化遗产 · 艺术 · 修复': 'Heritage · Art · Restoration',
                 '生活技艺 · 公益救护 · 户外': 'Life Skills · First Aid · Outdoors'}
        for gname, items in TRAIN_GROUPS:
            rows = []
            for it in items:
                _, date, title, _, _ = it
                if lang == 'zh':
                    rows.append(P(date, html.escape(strip_tags(title))))
                else:
                    t = en_of(strip_tags(title))
                    if not t:
                        MISSING.append('TRAIN: ' + title)
                        t = strip_tags(title)
                    rows.append(P(date, html.escape(t)))
            parts.append(block(
                ('研修' if lang == 'zh' else 'Programmes & Training') + ' · ' +
                (gname if lang == 'zh' else tr_en.get(gname, gname)),
                None, rows, None, None, True))
    else:
        # 精简版：获奖（单栏）+ 研修（双栏）
        for i, (title, note, rows, paras, chips) in enumerate(secs[5:7]):
            parts.append(block(title, note, rows, paras, chips, i == 1))

    # 末节：语言·方法·其他能力（两种版本都有）
    last = secs[-1]
    raw = list(last[1] or []) + list(last[2] or []) + list(last[3] or [])
    # 支持 ('S', 精简版专用) / ('F', 完整版专用) 标记
    paras = [(x[1] if isinstance(x, tuple) else x) for x in raw
             if (x[0] == 'F') == full if isinstance(x, tuple) or isinstance(x, str)]
    if variant == 'short':
        FOOT = {'zh': '简历所用材料（证书、录用函、成绩单、论文 PDF）均可按需要提供；个人网站含全部原件影印件。',
                'en': 'Certificates, transcripts and article PDFs available on request; originals on the personal website.'}[lang]
        parts.append('<div class="sec"><h2>%s</h2><div class="cols2">%s<p class="tag foot-in">%s</p></div></div>'
                     % (html.escape(last[0]), ''.join('<p class="tag">%s</p>' % x for x in paras), FOOT))
    else:
        parts.append(block(last[0], None, [], paras, None))

    if variant == 'full':
        note_method = {
            'zh': '简历所用材料（证书、录用函、成绩单、论文 PDF）均可按需要提供；个人网站含全部原件影印件。',
            'en': 'Certificates, transcripts and article PDFs available on request; originals on the personal website.',
        }[lang]
        parts.append('<div class="foot">%s</div>' % note_method)

    return '\n'.join(parts)


CSS = """
@page{size:A4;margin:12mm 13.5mm;}
html[lang="en"]@page{size:A4;margin:10.5mm 12mm;}
*{box-sizing:border-box}
body{margin:0;font-size:9.0pt;line-height:1.26;color:#1b1b1b;
 font-family:"Source Han Serif SC","Noto Serif SC","Songti SC",SimSun,Georgia,"Times New Roman",serif;}
.hd{display:flex;align-items:center;gap:14pt;border-bottom:1.1pt solid #b08b3a;padding-bottom:5pt;margin-bottom:1pt}
.hd-l{flex:1 1 auto;min-width:0}
.photo{flex:0 0 auto;width:16.5mm;height:22mm;object-fit:cover;border:.6pt solid #d8c58e}
.nm{font-size:17pt;letter-spacing:.08em;font-weight:700;line-height:1.1}
.nm .lt{font-size:10.5pt;letter-spacing:.1em;font-weight:400;color:#5c5c5c;font-family:Georgia,"Times New Roman",serif}
.role{margin-top:2.5pt;font-size:9.4pt;color:#3d3d3d}
.contact{margin-top:2.5pt;font-size:8.6pt;color:#555}
.sec{margin-top:9pt;break-inside:auto}
.sec h2{font-size:9.6pt;font-weight:700;letter-spacing:.13em;color:#8a6a22;margin:0 0 2.5pt;
 border-bottom:.55pt solid #cbb277;padding-bottom:1.5pt}
.note{font-size:8.6pt;color:#666;margin:0 0 3pt;line-height:1.28}
.tag{margin:1.5pt 0;font-size:9.1pt;color:#2b2b2b;line-height:1.33}
p.tag b,.tag b{font-weight:700}
.entry{display:flex;gap:8pt;margin-top:3.5pt;page-break-inside:avoid;break-inside:avoid}
.main{flex:1 1 auto;min-width:0}
.when{flex:0 0 auto;color:#666;font-size:8.6pt;padding-top:.4pt;white-space:nowrap}
.t{font-weight:600;line-height:1.28}
.sub{font-size:8.9pt;color:#333;margin-top:.8pt;line-height:1.3}
ul{margin:1.5pt 0 0;padding-left:11pt}
li{font-size:8.9pt;margin-top:.6pt}
.foot{margin-top:8pt;padding-top:4pt;border-top:.5pt solid #ddd;font-size:8.2pt;color:#777}
/* ---- 语言/方法块：双栏 ---- */
.cols2{columns:2;column-gap:16pt}
.cols2 p.tag{break-inside:avoid}
.foot-in{font-size:7.8pt;color:#888;margin-top:4pt}
/* ---- 英文版略收 ---- */
html[lang="en"] body{font-size:8.2pt;line-height:1.15}
html[lang="en"] .nm{font-size:16.5pt}
html[lang="en"] .sec h2{font-size:9.1pt}
html[lang="en"] .sec{margin-top:7.6pt}
html[lang="en"] .entry{margin-top:3pt}
html[lang="en"] .tag{font-size:8.2pt}
html[lang="en"] .sub,html[lang="en"] li{font-size:8.0pt}
/* ---- 英文精简版：再压紧一点，保证两页 ---- */
html[lang="en"] body.short{font-size:8.05pt;line-height:1.12}
html[lang="en"] body.short .sec{margin-top:6.6pt}
html[lang="en"] body.short .sec h2{font-size:9.0pt;margin-bottom:1.8pt;padding-bottom:1.2pt}
html[lang="en"] body.short .tag{font-size:8.05pt;line-height:1.26;margin:1pt 0}
html[lang="en"] body.short .entry{margin-top:2.4pt}
html[lang="en"] body.short .t{line-height:1.22}
html[lang="en"] body.short .sub,html[lang="en"] body.short li{font-size:7.9pt;line-height:1.22}
html[lang="en"] body.short .foot-in{margin-top:2.5pt;font-size:7.6pt}
html[lang="en"] body.short ul{margin-top:1pt}
/* ---- 完整版：密集 + 双栏 ---- */
body.full{font-size:8.9pt;line-height:1.26}
html[lang="en"] body.full{font-size:8.2pt;line-height:1.18}
html[lang="en"] body.full .t{font-size:8.1pt}
html[lang="en"] body.full .sub,html[lang="en"] body.full li{font-size:7.9pt}
html[lang="en"] body.full .tag{font-size:8.1pt}
body.full .sec{margin-top:7.5pt}
body.full .sec h2{font-size:9.2pt;margin-bottom:2pt}
body.full .entry{margin-top:2pt}
body.full .t{font-size:8.8pt}
body.full .sub{font-size:8.4pt}
body.full .tag{font-size:8.7pt}
body.full .when{font-size:8.3pt}
.cols{columns:2;column-gap:16pt}
.cols .entry{display:flex;gap:6pt}
.cols .when{font-size:8.2pt}
.cols .t{font-size:8.7pt;line-height:1.24}
body.short .cols .t{font-weight:400}
body.short .cols .entry{margin-top:1.6pt}
"""

TPL = """<!DOCTYPE html><html lang="%s"><head><meta charset="utf-8">
<title>%s</title><style>%s</style></head><body class="%s">%s</body></html>"""


def build():
    jobs = [('zh', 'short'), ('zh', 'full'), ('en', 'short'), ('en', 'full')]
    made = []
    for lang, var in jobs:
        body = render(lang, var)
        title = ('嵇鸿轩 · ' if lang == 'zh' else 'Hongxuan Ji · ') + TITLES[lang]['note_' + var]
        doc = TPL % (lang, title, CSS, (var + ' ' + lang), body)
        p = os.path.join(OUT, 'cv_%s_%s.html' % (lang, var))
        open(p, 'w', encoding='utf-8').write(doc)
        made.append(p)
        n = len(re.findall(r'class="entry"', body))
        print('%-16s entries=%d  bytes=%d' % (os.path.basename(p), n, len(doc)))
    if MISSING:
        print('\n-- 缺英文译文 %d 条（已回落中文）:' % len(MISSING))
        for m in MISSING[:25]:
            print('   ', m[:80])
    else:
        print('\n英文译文完整覆盖')
    return made


if __name__ == '__main__':
    build()
