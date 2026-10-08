#!/usr/bin/env python3
"""仓库校验脚本（Meta/verify.py；禁写词表与白名单以本文件为准）。
用法（在仓库根目录）：
  python3 Meta/verify.py . [相对路径 ...]   逐篇列出所给文件的结果，并报全库篇数与 FAIL 总数
  python3 Meta/verify.py .                  只报全库篇数与 FAIL 总数
  VERIFY_FLAGS=-v python3 Meta/verify.py .  另列出全库每条 FAIL
REPO 参数可以是仓库内任意目录：脚本用 git rev-parse --show-toplevel 定位仓库根；
省略 REPO 时取当前目录所在仓库，不在仓库内则取本脚本所在目录的上一级。
文件路径按仓库根写；从子目录运行时，按当前目录写的路径也会换算到仓库根。
对每个被跟踪（及未忽略的未跟踪）.md 做六项检查；只扫 .md，本脚本自身不在检查范围内。
项：禁写 / 断链 / 别名链 / 表格列数 / YAML / 外链与附件
Meta/ 规范本身会列举禁写词，禁写项对 Meta/ 只检查相对 origin/main 新增的行。
禁写项先按 WHITELIST（笔记名 → 正常用语短语）剔除再匹配。
依赖：Python 3 标准库 + PyYAML（YAML 项用 yaml.safe_load）。
"""
import os, re, subprocess, sys
try:
    import yaml
except ImportError:
    sys.exit('verify.py 需要 PyYAML（pip install pyyaml）以检查 frontmatter')

def _toplevel(d):
    r = subprocess.run(['git','-C',d,'rev-parse','--show-toplevel'],capture_output=True,text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None

_cwd = os.getcwd()
_args = sys.argv[1:]
if _args:
    repo = _toplevel(_args[0]) or os.path.abspath(_args[0])
    targets = _args[1:]
else:
    repo = _toplevel(_cwd) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = []
os.chdir(repo)

def _norm(t):
    # 按仓库根写的路径原样使用；仓库根下不存在而按当前目录存在的，换算成相对仓库根的路径
    if os.path.isabs(t) or os.path.exists(t):
        return t
    c = os.path.join(_cwd, t)
    if not os.path.exists(c):
        return t
    p = os.path.relpath(os.path.abspath(c), repo)
    return t if p.startswith('..') else p.replace(os.sep, '/')
targets = [_norm(t) for t in targets]

files = [f for f in subprocess.run(['git','-c','core.quotepath=off','ls-files','-co','--exclude-standard','*.md'],capture_output=True,text=True).stdout.split('\n') if f]
names = {}
for f in files:
    names.setdefault(os.path.basename(f)[:-3], []).append(f)

BAN = [
 ('派工', r'派工'), ('回头链', r'回头链'), ('立项', r'后续单独立项|若[^。]{0,20}立项'),
 ('波次', r'波次|\bWave\s*\d+|\bwave\d+'), ('验收', r'验收'), ('收口', r'收口'),
 ('本地路径', r'/workspace/|/tmp/|/home/\w|[A-Z]:\\\\'),
 ('体积', r'\d[\d,.]*\s*(字节|KB|MB|KiB|MiB)\b'), ('命令', r'\b(pdftotext|wget|curl|git clone|huggingface-cli)\b'),
 ('待办框', r'^\s*[-*]\s*\[[ xX]\]'),
 # 2026-10-09 主管要求补入的过程词（规范「正文禁写清单」第 1、4、5、10 条及写作者口吻）
 ('本卡', r'本卡'), ('补仓库', r'补仓库'), ('原篇原稿', r'原篇|原稿'),
 ('入库', r'(?:已|待|可|新|拟|未|随批|直接)入库|入库(?:政策|口吻|路径|动作|门槛|说明)'),
 ('跟读', r'跟读'), ('研究会', r'研究会|我方'),
 ('约束腔', r'禁止编造|不编造|一律锚定|议程硬禁|硬划界|禁止重写|与议程对齐'),
 ('交付', r'自检清单|完成判据|交付说明'), ('进度自述', r'本窗|已归档|再下载|起草：|修订时优先同步'),
]

# 白名单（主管 2026-10-08 裁定：被误报的正常用语不改）。按笔记名（不含路径，搬迁不失效）登记短语；
# 检查禁写前先从该笔记的行内剔除这些短语。只收正常用语，真违规不进白名单。
WHITELIST = {
 # 预取流程的收尾步骤名
 'HiCache层次化KV缓存': ['**收口**'],
 # 论文描述的 agent 行为，不是操作命令
 'Qwen3CoderNext技术报告深读': ['`git remote add` / `clone` / `curl`', '网络关键词（git/curl/wget）'],
 # 以下为内容本身的内存、显存、库体量数字，不是文件体积
 'Inspect评测Harness': ['**10MB**', '**100MB**'],
 # 主管 2026-10-09 裁定：A3 合并后白名单迁到新名（旧名条目已于 10-09 删除）
 '评测数据污染检测与可靠性': ['350MB / 100K tokens'],
 'AI基础设施总览': ['**192KB**'],
 'ThunderKittens内核DSL': ['**22MB**', '**689MB**', '**12.6MB**', '**TK \\<1.0MB**', '**\\>600MB**'],
 'MegaScaleInfer与UltraEP': ['**36 MB + 72 MB**'],
 'NVSHMEM与DeepEP通信': ['256B–64KiB'],
 'MobileLLM端侧增量': ['**590 MB**', '**720 MB**'],
 'TEE机密推理': ['**700 MB**'],
 '端侧小模型': ['**~8–32 MB**', '**8 MB**', '**24 MB**', '**~20MB SRAM**'],
 '长上下文位置编码与系统侧': ['**800 KB**'],
 'Gemma4技术报告深读': ['**400→200 MB**', '**390→87 MB'],
 # 主管 2026-10-09 裁定：每块缓存占用，论文 §2 原文数字（Hybrid Architectures），不是文件体积
 '混合Mamba与注意力架构设计菜谱': ['256 MiB 对 13.4 MiB'],
 # 主管 2026-10-08 裁定：每参数显存账（混合精度 Adam），不是文件体积
 '分布式训练并行策略': ['16 字节/参数', '各 2 字节', '共 12 字节'],
}

def whitelisted(f, l):
    for ph in WHITELIST.get(os.path.basename(f)[:-3], []):
        l = l.replace(ph, '')
    return l

def added_lines(f):
    out = subprocess.run(['git','diff','-U0','origin/main','--',f],capture_output=True,text=True).stdout
    return [l[1:] for l in out.split('\n') if l.startswith('+') and not l.startswith('+++')]

def strip_code(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', t)

def check(f):
    txt = open(f, encoding='utf-8').read()
    res = {}
    lines = added_lines(f) if f.startswith('Meta/') else txt.split('\n')
    hits = []
    for i,l in enumerate(lines,1):
        l = whitelisted(f, l)
        for k,p in BAN:
            if re.search(p, l): hits.append(f'{k}@{"+" if f.startswith("Meta/") else "L"}{i}')
    res['禁写'] = hits
    body = strip_code(txt)
    links = re.findall(r'\[\[([^\]]+)\]\]', body)
    res['别名链'] = [l for l in links if '|' in l]
    broken = []
    for l in links:
        n = l.split('|')[0].split('#')[0].strip()
        n = os.path.basename(n[:-3] if n.endswith('.md') else n)
        if n and n not in names: broken.append(n)
    res['断链'] = sorted(set(broken))
    bad = []; block = []
    def flush():
        if len(block) >= 2:
            cnt = [len(re.findall(r'(?<!\\)\|', re.sub(r'`[^`]*`','',x).strip().strip('|'))) for _,x in block]
            for (ln,x),c in zip(block,cnt):
                if c != cnt[0]: bad.append(f'L{ln}')
    for i,l in enumerate(txt.split('\n'),1):
        if l.lstrip().startswith('|'): block.append((i,l))
        else: flush(); block = []
    flush()
    res['表格列数'] = bad
    y = []
    if txt.startswith('---\n'):
        end = txt.find('\n---', 4)
        try: yaml.safe_load(txt[4:end])
        except Exception as e: y.append(str(e).split('\n')[0])
    res['YAML'] = y
    ext = re.findall(r'\]\((http://[^)]+)\)|<(http://[^>]+)>', txt)
    ext = [a or b for a,b in ext]
    res['外链与附件'] = ext
    return res

allres = {f: check(f) for f in files}
pdfs = [f for f in subprocess.run(['git','-c','core.quotepath=off','ls-files'],capture_output=True,text=True).stdout.split('\n') if re.search(r'\.pdf$|(^|/)(assets|_extract)/', f, re.I)]
total = sum(1 for r in allres.values() for v in r.values() if v) + len(pdfs)
for t in targets:
    r = allres.get(t) or check(t)
    print(f'== {t}')
    for k,v in r.items():
        print(f'  {k}: {"PASS" if not v else "FAIL " + "; ".join(map(str,v[:12]))}')
    print(f'  该文件 FAIL 数: {sum(1 for v in r.values() if v)}')
print(f'全库 .md {len(files)} 篇；被跟踪 PDF/附件 {len(pdfs)}；全库 FAIL 总数: {total}')
if '-v' in os.environ.get('VERIFY_FLAGS',''):
    for f,r in allres.items():
        for k,v in r.items():
            if v: print('FAIL', f, k, v[:5])
