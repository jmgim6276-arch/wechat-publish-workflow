---
name: wechat-publish-workflow
description: >
  Capture conversation material, incubate ideas, draft, style, publish, and update WeChat Official Account articles with a repeatable workflow.
  Use when the task involves 公众号 API 接入、IP 白名单排查、AppID/AppSecret 配置、触发“我要开始写公众号了”后的对话记录、
  将经历和情绪转化为文章、封面与正文样式联调、草稿新建或覆盖，或把这一整套流程整理成可复用的教学模板。
---

# WeChat Publish Workflow

Use this skill when the goal is to make a WeChat Official Account publishing pipeline actually work end to end, including the upstream authoring loop.

This skill has two linked layers:

1. authoring loop:
   - capture the user's spoken material
   - keep track of scenes, feelings, and judgments
   - decide when enough material exists to become an article
2. publish loop:
   - verify token first
   - identify real credential source
   - separate cover from正文
   - create or update draft deliberately
   - record the returned `media_id`

## Trigger Phrases

Use this skill immediately when the user says things like:

- `我要开始写公众号了`
- `帮我记录一下这次对话`
- `这段经历以后想写成文章`
- `先别写，先帮我攒素材`
- `把这些内容整理成公众号`

Treat these as the start of a capture workflow, not just a one-off writing request.

## Current Local Paths

- Skill-based account config: `/Users/tang/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md`
- Skill-based API credentials: `/Users/tang/.baoyu-skills/.env`
- Draft article workspace: `/Users/tang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Workshop/💼 工作时-工作台/零碳能源知识库/戴总的创业初心/公众号草稿/`
- Old publish toolkit: `/Users/tang/Desktop/02-技术外包项目/wechat-article-producer-repo/toolkit/`
- Cover template workspace: `/Users/tang/Desktop/AI写作工作流技能包/infographic-design/`
- Reference article about this workflow: `/Users/tang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Workshop/📓 睡前写-日记/2026年/4月/4月25日/4月25日.md`

## Main Workflow

### A. Start with capture, not structure

When the user begins in a conversational way, do not force an outline immediately.

First capture:

1. what happened
2. what the user felt
3. what the user realized
4. what sentence or judgment feels most true
5. whether this is a note, a reflection, or a teachable method

The capture rules and conversion logic live in [references/conversation-incubation.md](references/conversation-incubation.md).

### B. Decide if the material is ready

Material is usually ready to become an article when at least three things exist:

1. one clear emotional or situational trigger
2. one stable judgment the user actually believes
3. one scene, example, or contrast that makes the judgment concrete

If these do not exist yet, keep collecting instead of drafting too early.

### C. Convert before polishing

Once ready, convert the material into:

1. working title candidates
2. a short opening hook
3. 3 to 5 natural sections
4. one or two memorable lines
5. a closing line or question

For the full authoring loop, read [references/authoring-loop.md](references/authoring-loop.md).

### D. Only then enter publish operations

After the article direction is stable, switch into API and draft operations.

### 1. Check API health first

Run a direct token request before touching style or publish logic.

```bash
python3 - <<'PY'
import json, urllib.request
appid='YOUR_APP_ID'
secret='YOUR_APP_SECRET'
url=f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
print(json.dumps(json.loads(urllib.request.urlopen(url, timeout=20).read()), ensure_ascii=False, indent=2))
PY
```

Interpretation:

- `access_token` present: API chain is healthy
- `40164 invalid ip`: current公网IP is not in whitelist
- `40125 invalid appsecret`: wrong secret or wrong config source

For the full setup and whitelist procedure, read [references/setup-and-whitelist.md](references/setup-and-whitelist.md).

### 2. Verify which config file the active script really uses

Do not assume all publish scripts read the same secret.

There are usually two config patterns in this environment:

1. new skill-based config:
   - `~/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md`
   - `~/.baoyu-skills/.env`
2. old toolkit-specific config:
   - `.../toolkit/config.yaml`

If a script returns `invalid appsecret`, inspect the script before editing secrets.

### 3. Decide whether to create or update

- exploring a new direction: create a new draft
- refining the active working version: update the existing draft

For draft operations and media ID handling, read [references/draft-operations.md](references/draft-operations.md).

## Cover and正文 Are Separate Systems

Treat them separately.

- cover controls first-click recognition
-正文 controls reading comfort and completion rate

Do not assume fixing the cover fixes the article experience.

## Style Iteration Rule

When iterating, change one layer at a time:

1. background tone
2. typography
3. section rhythm
4. micro design elements
5. content density

If the user says "still not right", classify the problem first instead of changing everything.

For the current visual heuristics and working rules, read [references/style-iteration.md](references/style-iteration.md).

## Working Files in This Environment

- old bright正文 converter:
  `/Users/tang/Desktop/02-技术外包项目/wechat-article-producer-repo/toolkit/wechat_tech_converter.py`
- current refined正文 converter:
  `/Users/tang/Desktop/02-技术外包项目/wechat-article-producer-repo/toolkit/wechat_dark_editorial_converter.py`

If the user wants the whole article restyled, update the converter, not just the markdown body.

## What To Preserve

When a draft becomes active, preserve:

- article markdown path
- current `media_id`
- current `thumb_media_id`
- local manifest entry

Current manifest path:

`/Users/tang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Workshop/💼 工作时-工作台/零碳能源知识库/戴总的创业初心/公众号草稿/media_ids.json`

## Generalizing This for Teaching

When the user wants to share the process with others, package in this order:

1. trigger phrase and capture flow
2. material-to-article conversion flow
3. `.env.example`
4. `EXTEND.md` example
5. token test snippet
6. whitelist troubleshooting
7. create vs update draft workflow
8. style iteration rules

The teaching version should answer:

- when should AI start recording material
- what should be captured from a conversation
- how to know the material is mature enough
- how to turn lived experience into a readable article
- where AppID/AppSecret come from
- where to store them
- how to detect the current whitelist IP
- how to test connectivity quickly
- how to update a draft without creating duplicates

## Do Not

- do not turn every early conversation into an outline too fast
- do not confuse raw material collection with final writing
- do not force the user's lived experience into a corporate tone
- do not trust that the current IP is stable across retries
- do not overwrite a working draft unless the user intends that
- do not mix multiple visual grammars in正文 styling
- do not leave a new `media_id` unrecorded
- do not keep debugging long-read fatigue only through design; reduce content when density is the real issue
