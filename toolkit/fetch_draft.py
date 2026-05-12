#!/usr/bin/env python3
"""
fetch_draft.py — 从微信公众号草稿箱拉取当前草稿内容

核心用途：当戴总在手机上直接编辑草稿后，我们需要能看到他改了什么。

用法:
    # 用编号查
    python3 fetch_draft.py --id 03 --manifest /path/to/media_ids.json

    # 用 media_id 查
    python3 fetch_draft.py --media-id K02igswH...

    # 输出纯 HTML（原始微信格式）
    python3 fetch_draft.py --id 03 --manifest ... --format html

    # 输出转 Markdown（默认，人类可读）
    python3 fetch_draft.py --id 03 --manifest ... --format md

    # 和本地 MD 做 diff（最常用）
    python3 fetch_draft.py --id 03 --manifest ... --diff

    # 保存到文件（比如保存拉取到的当前版本）
    python3 fetch_draft.py --id 03 --manifest ... --format md --output /tmp/current.md

微信 API 文档:
    https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Get_draft.html
    POST /cgi-bin/draft/get?access_token=ACCESS_TOKEN
    body: { "media_id": "..." }
    response: {
        "news_item": [
            {
                "title": "...",
                "author": "...",
                "digest": "...",
                "content": "<HTML>",
                "thumb_media_id": "...",
                "url": "...",  // 草稿预览链接
                ...
            }
        ]
    }
"""
import sys
import os
import argparse
import json
import difflib
import urllib.request
import html as html_module
from pathlib import Path

SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from publish_article import load_config, get_access_token, parse_front_matter


def fetch_draft(token, media_id):
    """调 draft/get 拉取草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}"
    data = {"media_id": media_id}
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    raw = urllib.request.urlopen(req).read().decode("utf-8")
    resp = json.loads(raw)
    if resp.get("errcode", 0) not in (0, None):
        raise Exception(f"获取草稿失败: {resp}")
    return resp


def html_to_markdown(html_str):
    """把微信公众号的 HTML 转成人类可读的 Markdown"""
    import html2text
    h = html2text.HTML2Text()
    h.body_width = 0           # 不自动换行
    h.ignore_links = False
    h.ignore_images = False
    h.unicode_snob = True      # 保留中文字符
    h.single_line_break = False  # 段落之间保留空行，可读性好
    h.inline_links = True
    h.protect_links = False
    return h.handle(html_str)


def clean_markdown(md):
    """清理 html2text 转出来的 Markdown 里的一些噪声"""
    import re
    lines = md.split("\n")
    cleaned = []
    consecutive_empty = 0
    for line in lines:
        # 去掉行尾空格
        line = line.rstrip()
        # 去掉 html2text 常见的 escaping
        line = line.replace("\\.", ".").replace("\\_", "_").replace("\\-", "-")
        line = line.replace("\\*", "*").replace("\\(", "(").replace("\\)", ")")
        line = line.replace("\\[", "[").replace("\\]", "]")
        line = line.replace("\\!", "!").replace("\\#", "#")
        # html2text 会在 **加粗** 和标点（中/英/破折号）之间插入空格，去掉
        line = re.sub(r'\*\* ([。，！？；：、）】」』.,!?;:\)\]—–·])', r'**\1', line)
        line = re.sub(r'([（【「『.(\[—–·]) \*\*', r'\1**', line)
        # 最多保留 1 个连续空行（html2text 有时会产生 3+ 连续空行）
        if not line:
            consecutive_empty += 1
            if consecutive_empty > 1:
                continue
        else:
            consecutive_empty = 0
        cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def normalize_for_diff(text):
    """
    对内容做"语义规范化"，让 diff 只显示真正的文字变化。

    规范化策略：
    1. 去掉所有空行
    2. 去掉行首行尾空格
    3. 合并连续空格为单个空格
    4. 去掉 ** 加粗 和标点（含中文标点、英文标点、破折号）之间的空格
    5. 统一分隔线：* * * / --- / ***  → [HR]
    6. 统一斜体：_xxx_ / *xxx*  → [I:xxx]
    7. 去掉 _fetched_at 这类时间戳字段
    """
    import re
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 跳过 fetched_at / _source / _media_id 这类 fetch 时生成的字段
        if line.startswith("_fetched_at") or line.startswith("_source") or line.startswith("_media_id"):
            continue

        # 统一分隔线（--- / * * * / *** / ___）→ [HR]
        if re.match(r'^(\*\s*\*\s*\*|-{3,}|_{3,})$', line):
            lines.append("[HR]")
            continue

        # 多个空格 → 一个空格
        line = re.sub(r' {2,}', ' ', line)

        # ** 加粗后面/前面紧跟标点（中/英/破折号）时的空格
        # 破折号 —— · 中文标点 · 英文标点都算
        punct_after = r'。，！？；：、）】」』.,!?;:\)\]—–·'
        punct_before = r'（【「『.(\[—–·'
        line = re.sub(r'\*\*\s+([' + punct_after + r'])', r'**\1', line)
        line = re.sub(r'([' + punct_before + r'])\s+\*\*', r'\1**', line)

        # 统一斜体：把 _xxx_ 和 *xxx*（非加粗）都转成 [I:xxx]
        # html2text 默认把斜体转成 _xxx_，本地 MD 用 *xxx*
        # 先转 _xxx_ → [I:xxx]
        line = re.sub(r'(?<![*\w])_([^_\n]+?)_(?![*\w])', r'[I:\1]', line)
        # 再转 *xxx*（非 ** 开头）→ [I:xxx]
        line = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'[I:\1]', line)

        lines.append(line)
    return "\n".join(lines) + "\n"


def show_diff(local_md, remote_md, local_name="local", remote_name="draft-box"):
    """显示本地和远程的 unified diff"""
    local_lines = local_md.splitlines(keepends=True)
    remote_lines = remote_md.splitlines(keepends=True)
    diff = difflib.unified_diff(
        local_lines,
        remote_lines,
        fromfile=local_name,
        tofile=remote_name,
        n=3,  # 上下文行数
    )

    has_diff = False
    for line in diff:
        has_diff = True
        # 彩色输出（如果终端支持）
        if line.startswith("+++") or line.startswith("---"):
            print(f"\033[1m{line}\033[0m", end="")
        elif line.startswith("@@"):
            print(f"\033[36m{line}\033[0m", end="")
        elif line.startswith("+"):
            print(f"\033[32m{line}\033[0m", end="")
        elif line.startswith("-"):
            print(f"\033[31m{line}\033[0m", end="")
        else:
            print(line, end="")

    if not has_diff:
        print("\n\033[32m✓ 本地 MD 和草稿箱内容一致，没有差异。\033[0m")
    return has_diff


def resolve_from_manifest(manifest_path, article_id):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    article = manifest.get("articles", {}).get(article_id)
    if not article:
        raise ValueError(f"在 {manifest_path} 里找不到编号 {article_id}")
    manifest_dir = Path(manifest_path).parent
    return {
        "media_id": article["media_id"],
        "md_path": manifest_dir / article["file"],
        "title": article.get("title", ""),
    }


def strip_md_front_matter(md_text):
    """去掉 MD 的 front matter，只留正文，方便 diff"""
    _, body = parse_front_matter(md_text)
    return body


def main():
    parser = argparse.ArgumentParser(description="从微信草稿箱拉取当前草稿内容")
    parser.add_argument("--id", dest="article_id",
                        help="文章编号（01-10），配合 --manifest 使用")
    parser.add_argument("--manifest", help="media_ids.json 路径")
    parser.add_argument("--media-id", dest="media_id",
                        help="直接指定 media_id")
    parser.add_argument("--format", choices=["md", "html", "raw"], default="md",
                        help="输出格式：md（默认，转 Markdown）/ html（原始 HTML）/ raw（完整 JSON）")
    parser.add_argument("--diff", action="store_true",
                        help="和本地 MD 做 diff（只对 --id + --manifest 模式有效）")
    parser.add_argument("--sync-to-local", action="store_true",
                        help="把远程草稿同步回本地 MD（覆盖本地正文，保留 front matter 的自定义字段）")
    parser.add_argument("--output", "-o",
                        help="保存到文件（默认打印到 stdout）")
    parser.add_argument("--meta-only", action="store_true",
                        help="只显示标题/作者/摘要等元数据，不显示正文")
    args = parser.parse_args()

    # 确定 media_id
    local_md_path = None
    if args.article_id and args.manifest:
        info = resolve_from_manifest(args.manifest, args.article_id)
        media_id = info["media_id"]
        local_md_path = info["md_path"]
    elif args.media_id:
        media_id = args.media_id
    else:
        print("❌ 必须提供 --id + --manifest，或者 --media-id")
        sys.exit(1)

    # 加载配置 + 拿 token
    config = load_config()
    appid = config.get("wechat", {}).get("appid", "")
    secret = config.get("wechat", {}).get("secret", "")
    if not appid or not secret:
        print("❌ 缺少 config.yaml 中的 wechat.appid / wechat.secret")
        sys.exit(1)

    print(f"📥 正在从草稿箱拉取 media_id={media_id[:40]}...", file=sys.stderr)
    token = get_access_token(appid, secret)
    resp = fetch_draft(token, media_id)

    news_items = resp.get("news_item", [])
    if not news_items:
        print("❌ 返回的 news_item 为空，可能 media_id 无效或已删除")
        print(f"   完整响应: {json.dumps(resp, ensure_ascii=False, indent=2)}")
        sys.exit(1)

    item = news_items[0]
    title = item.get("title", "")
    author = item.get("author", "")
    digest = item.get("digest", "")
    content_html = item.get("content", "")
    preview_url = item.get("url", "")

    print(f"✓ 拉取成功: {title}", file=sys.stderr)
    print(f"  正文 HTML 长度: {len(content_html)} 字符", file=sys.stderr)
    print(file=sys.stderr)

    # --meta-only 模式
    if args.meta_only:
        output = f"""# 草稿元数据

**标题**: {title}
**作者**: {author}
**摘要**: {digest}
**预览链接**: {preview_url}
**正文长度**: {len(content_html)} 字符
"""
        _emit(output, args.output)
        return

    # raw 模式：打印完整 JSON
    if args.format == "raw":
        _emit(json.dumps(resp, ensure_ascii=False, indent=2), args.output)
        return

    # html 模式：打印原始 HTML
    if args.format == "html":
        _emit(content_html, args.output)
        return

    # md 模式：HTML → Markdown
    md_body = html_to_markdown(content_html)
    md_body = clean_markdown(md_body)

    md_output = f"""---
title: "{title}"
author: "{author}"
summary: "{digest}"
_fetched_at: "{_now()}"
_source: "draft-box-fetch"
_media_id: "{media_id}"
---

{md_body}"""

    # --sync-to-local 模式：把远程内容写回本地 MD
    if args.sync_to_local:
        if not local_md_path or not local_md_path.exists():
            print(f"❌ --sync-to-local 需要本地 MD 文件: {local_md_path}")
            sys.exit(1)

        import yaml as _yaml
        # 读本地的 front matter，保留自定义字段（cover_accent、series 等）
        local_raw = local_md_path.read_text(encoding="utf-8")
        local_meta, _ = parse_front_matter(local_raw)

        # 用远程的最新 title/author/summary 覆盖 front matter 里对应字段
        # 保留本地特有的 cover_accent / series / 其他字段
        new_meta = dict(local_meta)
        new_meta["title"] = title
        new_meta["author"] = author
        new_meta["summary"] = digest
        new_meta["_last_synced_from_draft"] = _now()

        # 转换为 Markdown 正文（规范化清理后的版本）
        remote_body_md = html_to_markdown(content_html)
        remote_body_md = clean_markdown(remote_body_md)

        # 拼回 front matter + 新正文
        fm_yaml = _yaml.dump(new_meta, allow_unicode=True,
                             default_flow_style=False, sort_keys=False)
        new_content = f"---\n{fm_yaml}---\n\n{remote_body_md}"

        # 备份旧文件
        backup_path = local_md_path.with_suffix(
            f".backup-{_now().replace(':', '').replace(' ', '_')}.md")
        backup_path.write_text(local_raw, encoding="utf-8")

        # 写入新内容
        local_md_path.write_text(new_content, encoding="utf-8")

        print(f"✅ 已把远程草稿同步回本地:")
        print(f"   {local_md_path}")
        print(f"")
        print(f"   备份文件: {backup_path.name}")
        print(f"   新字段: _last_synced_from_draft = {new_meta['_last_synced_from_draft']}")
        print(f"")
        print(f"   下次改本地 MD 时是基于这个最新版本，不会覆盖戴总的修改")
        return

    # --diff 模式：对比本地
    if args.diff:
        if not local_md_path or not local_md_path.exists():
            print(f"❌ --diff 需要本地 MD 文件，但找不到: {local_md_path}")
            sys.exit(1)

        local_raw = local_md_path.read_text(encoding="utf-8")
        local_body = strip_md_front_matter(local_raw)
        remote_body = strip_md_front_matter(md_output)

        # 规范化：去掉空行、去掉格式化差异，只留下真正的文字差异
        local_normalized = normalize_for_diff(local_body)
        remote_normalized = normalize_for_diff(remote_body)

        print(f"📊 对比 [本地 MD] ↔ [草稿箱当前内容]", file=sys.stderr)
        print(f"   (已规范化，忽略空行和格式化差异)", file=sys.stderr)
        print(file=sys.stderr)
        show_diff(
            local_normalized,
            remote_normalized,
            local_name=f"local/{local_md_path.name}",
            remote_name=f"draft-box/{args.article_id or media_id[:10]}",
        )
        return

    # 默认：打印完整的 Markdown
    _emit(md_output, args.output)


def _emit(text, output_path):
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
        print(f"✓ 已保存到: {output_path}", file=sys.stderr)
    else:
        print(text)


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
