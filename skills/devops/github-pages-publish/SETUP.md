# 一次性初始化：创建仓库 + 开通 GitHub Pages

> 这些步骤**只做一次**，不属于日常发布流程。日常推送用 `scripts/publish.py`。
> 需要 `gh` CLI 已登录（`gh auth status`）。

## 1. 创建仓库

```bash
gh repo create <owner>/<repo> --public --description "..."
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

## 2. 放首个内容 + 首次推送

GitHub Pages 要求 `main` 分支存在才能开通，所以先推一个 `index.html`：

```bash
touch .nojekyll          # 关掉 Jekyll 处理，直接把仓库当静态站
echo '<!doctype html><meta charset=utf-8><h1>Hello</h1>' > index.html
git add -A && git commit -m "Initial page" && git branch -M main && git push -u origin main
```

## 3. 开通 GitHub Pages（main 分支根目录）

```bash
gh api -X POST repos/<owner>/<repo>/pages \
  -f "source[branch]=main" -f "source[path]=/"
```

首次构建约 1-2 分钟。上线地址：`https://<owner>.github.io/<repo>/`

```bash
# 轮询构建状态直到 built
gh api repos/<owner>/<repo>/pages --jq '.status'
```

## 完成后

之后每次更新内容，用日常发布脚本：

```bash
python3 scripts/publish.py --repo-dir /path/to/repo \
  --pages-url https://<owner>.github.io/<repo> \
  --files page.html index.html --message "Publish ..."
```

## 备注

- 私有仓库开 Pages 需要 GitHub Pro；公开仓库免费。
- 删除并重建仓库需要 token 带 `delete_repo` scope（`gh auth refresh -s delete_repo`），或在网页 Settings → Danger Zone 手动删。
