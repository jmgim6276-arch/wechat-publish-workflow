#!/usr/bin/env python3
"""
update_article.py — 更新已有的公众号草稿（覆盖原草稿，不会产生重复）

用法:
    # 方式 A：直接指定 media_id
    python3 update_article.py article.md --media-id K02igswH...

    # 方式 B：用编号从 media_ids.json 里查
    python3 update_article.py --id 03 \
        --manifest "/path/to/公众号草稿/media_ids.json"

    # 更新封面
    python3 update_article.py --id 03 --manifest /path/to/media_ids.json \
        --cover new-cover.png

微信 API 文档:
    https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Update_draft.html
    POST https://api.weixin.qq.com/cgi-bin/draft/update?access_token=ACCESS_TOKEN
    body: { "media_id": "...", "index": 0, "articles": { ... } }
"""
import sys
import os
import argparse
import json
import yaml
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

# 复用 publish_article.py 里的几个函数
from publish_article import (
    load_config,
    parse_front_matter,
    get_access_token,
    upload_thumb,
    convert_md_to_html,
)


def update_draft(token, media_id, index, title, content, thumb_media_id,
                 author="", digest=""):
    """
    更新草稿里指定 index 的文章。
    单篇文章的草稿 index = 0。
    """
    url = f"https://api.weixin.qq.com/cgi-bin/draft/update?access_token={token}"
    data = {
        "media_id": media_id,
        "index": index,
        "articles": {
            "title": title[:64],
            "author": author,
            "digest": digest[:120] if digest else "",
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }
    }
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    resp = json.loads(urllib.request.urlopen(req).read())

    if resp.get("errcode", 0) == 0:
        return True
    raise Exception(f"更新草稿失败: {resp}")


def get_existing_draft_thumb(token, media_id):
    """
    读取现有草稿里的 thumb_media_id，以便不重新上传封面时复用。
    """
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}"
    data = {"media_id": media_id}
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        news_item = resp.get("news_item", [])
        if news_item and isinstance(news_item, list):
            return news_item[0].get("thumb_media_id", "")
    except Exception as e:
        print(f"   ⚠ 读取现有封面失败: {e}")
    return ""


def resolve_from_manifest(manifest_path, article_id):
    """从 media_ids.json 里根据编号查找文章信息"""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    article = manifest.get("articles", {}).get(article_id)
    if not article:
        raise ValueError(f"在 {manifest_path} 里找不到编号 {article_id}")

    manifest_dir = Path(manifest_path).parent
    return {
        "media_id": article["media_id"],
        "md_path": manifest_dir / article["file"],
        "cover_path": manifest_dir / article["cover"],
    }


def main():
    parser = argparse.ArgumentParser(description="更新已有的公众号草稿")
    parser.add_argument("input", nargs="?", help="Markdown 文件路径")
    parser.add_argument("--id", dest="article_id",
                        help="文章编号（01-10），配合 --manifest 使用")
    parser.add_argument("--manifest", help="media_ids.json 路径")
    parser.add_argument("--media-id", dest="media_id", help="直接指定 media_id")
    parser.add_argument("--index", type=int, default=0, help="多图文草稿的 index，默认 0")
    parser.add_argument("--theme", default="tech-modern")
    parser.add_argument("--cover", help="新封面图路径（不指定则复用原封面）")
    parser.add_argument("--title", help="覆盖标题")
    parser.add_argument("--author", help="覆盖作者")
    parser.add_argument("--digest", help="覆盖摘要")
    parser.add_argument("--dry-run", action="store_true",
                        help="只解析不推送，用于调试")
    args = parser.parse_args()

    # 1. 确定目标 media_id 和 md 路径
    print("📋 [1/6] 确定更新目标...")
    if args.article_id and args.manifest:
        info = resolve_from_manifest(args.manifest, args.article_id)
        media_id = info["media_id"]
        md_path = info["md_path"]
        default_cover = info["cover_path"]
        print(f"   从 manifest 查到: {md_path.name}")
    elif args.media_id and args.input:
        media_id = args.media_id
        md_path = Path(args.input)
        default_cover = None
    else:
        print("❌ 必须提供 --id + --manifest，或者 --media-id + <input>")
        sys.exit(1)

    if not md_path.exists():
        print(f"❌ Markdown 文件不存在: {md_path}")
        sys.exit(1)

    print(f"   media_id: {media_id[:40]}...")

    # 2. 加载配置
    print("⚙  [2/6] 加载配置...")
    config = load_config()
    appid = config.get("wechat", {}).get("appid", "")
    secret = config.get("wechat", {}).get("secret", "")
    if not appid or not secret:
        print("❌ 缺少 config.yaml 中的 wechat.appid / wechat.secret")
        sys.exit(1)

    # 3. 解析 Markdown
    print("📝 [3/6] 解析 Markdown...")
    md_text = md_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(md_text)

    title = args.title or meta.get("title", "") or md_path.stem
    author = args.author or meta.get("author", "") or config.get("wechat", {}).get("author", "")
    digest = args.digest or meta.get("summary", "") or body[:100].replace("\n", " ")

    print(f"   标题: {title}")
    print(f"   作者: {author}")
    print(f"   摘要: {digest[:50]}...")

    # 4. 转 HTML
    print("🎨 [4/6] 转换为微信格式 HTML...")
    html, _ = convert_md_to_html(body, theme=args.theme)
    print(f"   HTML 长度: {len(html)} 字符")

    if args.dry_run:
        print("\n⏭  [DRY RUN] 解析完成但不实际推送。")
        print(f"   即将用此内容覆盖 media_id: {media_id}")
        return

    # 5. 获取 token + 处理封面
    print("🔑 [5/6] 获取 access_token + 处理封面...")
    token = get_access_token(appid, secret)
    print("   ✅ token 获取成功")

    cover_path = None
    if args.cover:
        cover_path = args.cover
    elif default_cover and default_cover.exists():
        cover_path = str(default_cover)

    if cover_path and os.path.exists(cover_path):
        print(f"   上传新封面: {cover_path}")
        thumb_media_id = upload_thumb(token, cover_path)
        print(f"   ✅ 新封面 media_id: {thumb_media_id[:20]}...")
    else:
        print("   复用原草稿里的封面...")
        thumb_media_id = get_existing_draft_thumb(token, media_id)
        if not thumb_media_id:
            print("   ⚠ 无法获取原封面，更新可能失败")
        else:
            print(f"   ✅ 原封面 media_id: {thumb_media_id[:20]}...")

    # 6. 更新草稿
    print("🚀 [6/6] 更新草稿箱...")
    update_draft(token, media_id, args.index, title, html,
                 thumb_media_id, author, digest)

    print()
    print("═" * 50)
    print("✅ 更新成功！")
    print("═" * 50)
    print(f"  📝 标题:    {title}")
    print(f"  👤 作者:    {author}")
    print(f"  📦 media_id: {media_id}")
    print()
    print("  👉 登录 mp.weixin.qq.com → 内容管理 → 草稿箱 查看")
    print("     草稿已直接覆盖，不会产生重复")
    print()


if __name__ == "__main__":
    main()
