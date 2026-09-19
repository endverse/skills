#!/usr/bin/env python3
"""
render.py — 把结构化 JSON 渲染成复古编辑部杂志风的独立 HTML（零依赖，纯标准库）。

通用渲染器：不绑定任何具体主题（AI/新闻/周报皆可）。品牌名、副标题、板块、
条目全部由输入 JSON 决定。样式为冻结的「杂志风」设计系统。

输入 JSON schema（brief.json）:
{
  "brand": "AI & 基础设施早报",         # 报头主标题
  "date_label": "2026 年 09 月 19 日 · 星期六",
  "issue": 1,                            # 期号，可选
  "kicker": "DAILY BRIEFING",           # 英文角标，可选
  "lead": "今日一句话综述…",             # 导语，可选
  "footer": "由 XX 自动汇编 · 每日更新",  # 页脚，可选
  "highlights": [                        # 🔥 重点，0-N 条，可选
    {"title","url","summary","note"}     # note = 次级要点块（可选）
  ],
  "sections": [                          # 板块（有序），每个板块含分类
    {
      "label": "🤖 AI 板块",             # 板块大标签（可选，多板块时用）
      "categories": [
        {"emoji":"🧠","title":"模型与研究","en":"Models",
         "items":[{"title","url","summary","tag","source","oss":false}]}
      ]
    }
  ],
  "flash": [ {"title","url"} ]            # 快讯，可选
}

用法: python3 render.py brief.json output.html
"""
import json, html, sys, os

STYLE = """  :root{
    --ink:#15130f; --paper:#e9e2d6; --red:#d7382f; --sub:#6d6459;
    --line:#c9bfae; --card:#f3eee3; --tagbg:#e4dccc;
  }
  *{margin:0;padding:0;box-sizing:border-box;-webkit-text-size-adjust:100%}
  html,body{background:#d8cfbe}
  body{color:var(--ink);font-family:"Noto Serif SC","Songti SC",SimSun,serif;
    line-height:1.8;font-size:16px;
    background:radial-gradient(circle at 30% 12%, rgba(255,255,255,.28), transparent 30%),
      linear-gradient(135deg, rgba(21,19,15,.035) 0 1px, transparent 1px 8px),var(--paper);
    padding:0 0 70px;}
  .paper{max-width:680px;margin:0 auto;
    background:radial-gradient(circle at 70% 8%, rgba(255,255,255,.22), transparent 34%),var(--paper);
    box-shadow:0 0 40px rgba(21,19,15,.12);min-height:100vh}
  .masthead{padding:30px 28px 22px;border-bottom:3px double var(--ink)}
  .brandbar{display:flex;justify-content:space-between;align-items:center;
    font-size:12px;letter-spacing:2px;color:var(--sub);text-transform:uppercase}
  .issue-badge{background:var(--red);color:#fff;padding:3px 10px;font-weight:700;
    letter-spacing:1px;border-radius:2px}
  .title{font-size:46px;font-weight:900;letter-spacing:3px;line-height:1.15;margin:14px 0 6px;text-align:center}
  .title .amp{color:var(--red)}
  .dateline{text-align:center;font-size:13px;letter-spacing:4px;color:var(--sub);
    display:flex;align-items:center;justify-content:center;gap:12px}
  .dateline::before,.dateline::after{content:"";height:1px;width:40px;background:var(--line)}
  .lead{padding:20px 28px;font-size:15px;color:#3a352d;border-bottom:1px dashed var(--line);position:relative}
  .lead .q{font-size:52px;color:var(--red);font-weight:900;line-height:0;
    position:relative;top:14px;margin-right:4px;font-family:Georgia,serif}
  .hot{padding:24px 28px;border-bottom:1px dashed var(--line);
    background:linear-gradient(180deg,rgba(215,56,47,.05),transparent)}
  .hot-kicker{display:inline-block;background:var(--ink);color:var(--paper);
    font-size:12px;letter-spacing:3px;padding:4px 12px;font-weight:700;margin-bottom:14px}
  .hot h2{font-size:26px;font-weight:900;line-height:1.35;margin-bottom:10px}
  .hot h2 a{color:var(--ink);text-decoration:none;border-bottom:3px solid var(--red)}
  .hot p{font-size:15px;color:#3a352d;margin-bottom:8px}
  .hot .note{font-size:14px;color:var(--sub);border-left:3px solid var(--red);padding-left:12px;margin-top:10px}
  .section{padding:22px 28px 6px}
  .sec-head{display:flex;align-items:baseline;gap:10px;margin-bottom:4px;
    border-bottom:2px solid var(--ink);padding-bottom:6px}
  .sec-emoji{font-size:20px}
  .sec-title{font-size:21px;font-weight:900;letter-spacing:1px}
  .sec-en{margin-left:auto;font-size:11px;letter-spacing:2px;color:var(--sub);text-transform:uppercase}
  .board-label{text-align:center;font-size:13px;letter-spacing:6px;color:var(--red);
    font-weight:700;padding:26px 0 4px;text-transform:uppercase}
  .board-label span{border-bottom:2px solid var(--red);padding-bottom:4px}
  .item{padding:15px 0;border-bottom:1px dashed var(--line);display:flex;gap:14px}
  .item:last-child{border-bottom:none}
  .num{font-size:22px;font-weight:900;color:var(--red);line-height:1.2;min-width:30px;font-family:Georgia,serif}
  .item-body{flex:1}
  .item h3{font-size:17px;font-weight:700;line-height:1.5;margin-bottom:5px}
  .item h3 a{color:var(--ink);text-decoration:none}
  .item h3 a:hover{color:var(--red)}
  .item p{font-size:14.5px;color:#4a453c;margin-bottom:8px}
  .meta{font-size:12px;color:var(--sub);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .tag{background:var(--tagbg);color:#6a5f4d;padding:2px 9px;border-radius:2px;font-size:11px;letter-spacing:1px}
  .tag.oss{background:#dfe8d8;color:#4a6b3a}
  .src{color:var(--red);text-decoration:none;font-weight:500}
  .src::after{content:" ↗";font-size:10px}
  .flash{padding:20px 28px}
  .flash-title{font-size:15px;font-weight:900;letter-spacing:2px;margin-bottom:10px;color:var(--sub)}
  .flash ul{list-style:none}
  .flash li{font-size:14px;padding:7px 0;border-bottom:1px dotted var(--line);display:flex;gap:8px}
  .flash li::before{content:"▪";color:var(--red);flex-shrink:0}
  .flash li a{color:var(--ink);text-decoration:none}
  .flash li a:hover{color:var(--red);text-decoration:underline}
  .footer{padding:28px;text-align:center;border-top:3px double var(--ink);margin-top:14px}
  .footer .logo{font-size:18px;font-weight:900;letter-spacing:2px;margin-bottom:6px}
  .footer .logo .amp{color:var(--red)}
  .footer p{font-size:12px;color:var(--sub);letter-spacing:1px;line-height:1.9}
  @media (max-width:480px){.title{font-size:36px}.hot h2{font-size:22px}
    .section,.masthead,.lead,.hot,.flash{padding-left:20px;padding-right:20px}}"""

def esc(s): return html.escape(s or "", quote=True)

def render_item(n, it):
    tags = ""
    if it.get("oss"): tags += '<span class="tag oss">🔧 开源</span>'
    if it.get("tag"): tags += f'<span class="tag">{esc(it["tag"])}</span>'
    src = f'<a class="src" href="{esc(it["url"])}" target="_blank" rel="noopener">{esc(it.get("source",""))}</a>' if it.get("source") else ""
    return f"""    <div class="item">
      <div class="num">{n:02d}</div>
      <div class="item-body">
        <h3><a href="{esc(it['url'])}" target="_blank" rel="noopener">{esc(it['title'])}</a></h3>
        <p>{esc(it.get('summary',''))}</p>
        <div class="meta">{tags}{src}</div>
      </div>
    </div>"""

def render(d):
    p = []
    brand = d.get("brand","Briefing")
    p.append(f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(brand)} · {esc(d.get('date_label',''))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
{STYLE}
</style>
</head>
<body>
<div class="paper">
  <header class="masthead">
    <div class="brandbar"><span>{esc(d.get('kicker',''))}</span>{f'<span class="issue-badge">第 {d["issue"]:03d} 期</span>' if d.get('issue') else ''}</div>
    <h1 class="title">{esc(brand)}</h1>
    <div class="dateline">{esc(d.get('date_label',''))}</div>
  </header>""")
    if d.get("lead"):
        p.append(f'  <div class="lead"><span class="q">“</span>{esc(d["lead"])}</div>')
    for h in d.get("highlights", []):
        note = f'<div class="note">{esc(h["note"])}</div>' if h.get("note") else ""
        p.append(f"""  <div class="hot">
    <span class="hot-kicker">🔥 今日重点</span>
    <h2><a href="{esc(h['url'])}" target="_blank" rel="noopener">{esc(h['title'])}</a></h2>
    <p>{esc(h.get('summary',''))}</p>
    {note}
  </div>""")
    multi = len([s for s in d.get("sections",[]) if s.get("label")]) > 0
    for sec in d.get("sections", []):
        if sec.get("label") and multi:
            p.append(f'  <div class="board-label"><span>{esc(sec["label"])}</span></div>')
        n = 1
        for cat in sec.get("categories", []):
            if not cat.get("items"): continue
            en = f'<span class="sec-en">{esc(cat.get("en",""))}</span>' if cat.get("en") else ""
            p.append(f'''  <section class="section">
    <div class="sec-head"><span class="sec-emoji">{esc(cat.get("emoji",""))}</span><span class="sec-title">{esc(cat["title"])}</span>{en}</div>''')
            for it in cat["items"]:
                p.append(render_item(n, it)); n += 1
            p.append('  </section>')
    if d.get("flash"):
        p.append('  <div class="flash">\n    <div class="flash-title">⚡ 快讯速览</div>\n    <ul>')
        for f in d["flash"]:
            p.append(f'      <li><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["title"])}</a></li>')
        p.append('    </ul>\n  </div>')
    if d.get("footer"):
        p.append(f"""  <footer class="footer">
    <div class="logo">{esc(brand)}</div>
    <p>{esc(d["footer"])}</p>
  </footer>""")
    p.append("</div>\n</body>\n</html>")
    return "\n".join(p)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("用法: python3 render.py brief.json output.html")
    data = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    # 自动创建输出文件的父目录（支持 2026/2026-09-20.html 这类年份归档路径）
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    open(out, "w").write(render(data))
    print(f"已渲染 {out}")
