#!/usr/bin/env python3
"""
send_card.py — 构造并发送飞书 Card 2.0 交互卡片（封面图 + 正文块 + 跳转按钮）。

通用飞书卡片推送：任何"封面+摘要+按钮跳转"的通知场景都能用（日报/周报/告警/发布通知）。
依赖 lark-cli（已认证 bot 身份）。图片上传、image_key 注入、dry-run 校验、正式发送一条龙。

输入 spec.json:
{
  "chat_id": "oc_xxx",            # 或 "user_id": "ou_xxx"（二选一）
  "header": {"title": "...", "subtitle": "...", "template": "indigo", "icon": "myai_colorful"},
  "cover_image": "/abs/path/to/cover.png",   # 可选，本地封面图，自动上传
  "blocks": [                     # 正文块，按顺序渲染
    {"type": "markdown", "content": "**🔥 今日重点**\n..."},
    {"type": "hr"},
    {"type": "markdown", "content": "**今日看点**\n..."},
    {"type": "grey", "content": "共 N 条"}     # 灰字（Card2.0 无 note 标签，用灰字 markdown 代替）
  ],
  "button": {"text": "📖 阅读全文", "url": "https://..."},
  "footer": "由 XX 自动汇编"      # 可选灰字页脚
}

用法:
  python3 send_card.py spec.json            # dry-run + 正式发送
  python3 send_card.py spec.json --dry-run  # 只校验不发送
"""
import json, sys, subprocess, tempfile, os

def upload_image(path):
    """上传本地图片拿 image_key。lark-cli 要求 cwd 相对路径。"""
    d, fn = os.path.split(os.path.abspath(path))
    r = subprocess.run(["lark-cli","im","images","create","--data",'{"image_type":"message"}',
                        "--file", f"./{fn}"], cwd=d, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["data"]["image_key"]
    except Exception:
        sys.exit(f"封面上传失败: {r.stdout}\n{r.stderr}")

def build_card(spec, image_key=None):
    els = []
    if image_key:
        els.append({"tag":"img","img_key":image_key,
                    "alt":{"tag":"plain_text","content":"封面"},
                    "mode":"fit_horizontal","preview":True})
    for b in spec.get("blocks", []):
        t = b.get("type")
        if t == "hr":
            els.append({"tag":"hr"})
        elif t == "grey":
            els.append({"tag":"markdown","content":f"<font color='grey'>{b['content']}</font>"})
        else:  # markdown
            els.append({"tag":"markdown","content":b["content"]})
    btn = spec.get("button")
    if btn:
        els.append({"tag":"button","text":{"tag":"plain_text","content":btn["text"]},
                    "type":"primary","width":"fill",
                    "behaviors":[{"type":"open_url","default_url":btn["url"]}]})
    if spec.get("footer"):
        els.append({"tag":"hr"})
        els.append({"tag":"markdown","content":f"<font color='grey'>{spec['footer']}</font>"})
    h = spec.get("header", {})
    header = {"template": h.get("template","indigo"),
              "title":{"tag":"plain_text","content":h.get("title","")}}
    if h.get("subtitle"): header["subtitle"]={"tag":"plain_text","content":h["subtitle"]}
    if h.get("icon"): header["icon"]={"tag":"standard_icon","token":h["icon"]}
    return {"schema":"2.0","config":{"wide_screen_mode":True},"header":header,
            "body":{"elements":els}}

def send(spec, card, dry_run):
    target = ["--chat-id", spec["chat_id"]] if spec.get("chat_id") else ["--user-id", spec["user_id"]]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(card, f, ensure_ascii=False); cardfile = f.name
    cmd = ["lark-cli","im","+messages-send",*target,"--msg-type","interactive",
           "--content", open(cardfile).read(), "--as","bot"]
    if dry_run: cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(cardfile)
    try:
        out = json.loads(r.stdout)
    except Exception:
        sys.exit(f"发送异常: {r.stdout}\n{r.stderr}")
    return out

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    dry_only = "--dry-run" in sys.argv
    image_key = upload_image(spec["cover_image"]) if spec.get("cover_image") else None
    card = build_card(spec, image_key)
    # 先 dry-run
    dr = send(spec, card, dry_run=True)
    if not dr.get("ok"):
        sys.exit(f"dry-run 未通过: {dr.get('error',{}).get('message','')}")
    print("dry-run ✅")
    if dry_only:
        print("仅 dry-run，未发送。"); sys.exit(0)
    res = send(spec, card, dry_run=False)
    if res.get("ok"):
        print(f"发送成功 ✅ message_id={res.get('data',{}).get('message_id','')}")
    else:
        sys.exit(f"发送失败: {res.get('error',{}).get('message','')}")
