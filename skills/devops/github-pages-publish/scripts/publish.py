#!/usr/bin/env python3
"""
publish.py — 把本地文件发布到一个已存在的 GitHub Pages 仓库，并校验线上==本地。

日常推送用。前提：仓库已创建、GitHub Pages 已开通（一次性动作见 SETUP.md）。
只做「add → commit → push → 等构建 → 校验线上 hash 与本地一致」。

用法:
  python3 publish.py --repo-dir /path/to/repo --pages-url https://user.github.io/repo \\
                     --files a.html index.html --message "Publish 2026-09-19"

  --files 省略则提交仓库内所有改动。
"""
import argparse, subprocess, sys, os, hashlib, ssl, time, urllib.request

def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-dir", required=True)
    ap.add_argument("--pages-url", required=True, help="如 https://user.github.io/repo")
    ap.add_argument("--files", nargs="*", help="要提交的文件；省略=全部改动")
    ap.add_argument("--message", required=True)
    ap.add_argument("--verify-file", help="用于线上==本地校验的文件名(默认取 --files 第一个)")
    args = ap.parse_args()

    repo = os.path.abspath(os.path.expanduser(args.repo_dir))
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"不是 git 仓库: {repo}")

    # add
    if args.files:
        sh(["git","add",*args.files], cwd=repo)
    else:
        sh(["git","add","-A"], cwd=repo)
    # 有改动才提交
    if sh(["git","diff","--cached","--quiet"], cwd=repo).returncode == 0:
        print("无改动，跳过提交。")
    else:
        c = sh(["git","commit","-m",args.message], cwd=repo)
        if c.returncode != 0:
            sys.exit(f"commit 失败: {c.stdout}\n{c.stderr}")
    p = sh(["git","push"], cwd=repo)
    if p.returncode != 0:
        sys.exit(f"push 失败: {p.stdout}\n{p.stderr}")
    print("已 push。")

    # 校验线上==本地
    vf = args.verify_file or (args.files[0] if args.files else None)
    if not vf:
        print("未指定校验文件，跳过线上校验。"); return
    local_path = os.path.join(repo, vf)
    if not os.path.exists(local_path):
        print(f"本地无 {vf}，跳过校验。"); return
    local = hashlib.sha256(open(local_path,"rb").read()).hexdigest()
    url = args.pages_url.rstrip("/") + "/" + vf
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    for i in range(8):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15, context=ctx).read()
            if hashlib.sha256(data).hexdigest() == local:
                print(f"✅ 线上 == 本地: {url}"); return
        except Exception:
            pass
        time.sleep(12)
    print(f"⚠️ 线上尚未与本地一致(Pages 可能仍在构建): {url}")

if __name__ == "__main__":
    main()
