# gongzhhao.project

公众号工作流项目，采用 **skill + toolkit** 的互补结构：

- `skills/wechat-publish-workflow-skill/`：AI 工作流入口，负责素材采集、成稿判断、风格迭代、API/白名单/凭据排查
- `toolkit/`：真实执行层，负责发布、更新、回拉、正文转换、封面生成
- `docs/公众号工作流接入方案.md`：接线与职责分层说明

## 适用场景

适用于：
- 公众号选题与素材孵化
- 把对话/经历整理成公众号文章
- 微信公众号草稿发布与更新
- 封面与正文样式调优
- 戴总修改后回拉同步本地稿件

---

## 仓库结构

```text
.
├── README.md
├── docs/
│   └── 公众号工作流接入方案.md
├── skills/
│   └── wechat-publish-workflow-skill/
└── toolkit/
    ├── config.yaml.example
    ├── fetch_draft.py
    ├── make_cover.py
    ├── publish_article.py
    ├── requirements.txt
    ├── update_article.py
    └── wechat_tech_converter.py
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/jmgim6276-arch/gongzhhao.project
cd gongzhhao.project
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv ~/.wechat-venv
~/.wechat-venv/bin/pip install -r toolkit/requirements.txt
```

### 3. 配置公众号凭据

```bash
cp toolkit/config.yaml.example toolkit/config.yaml
```

然后编辑 `toolkit/config.yaml`，填入：
- `appid`
- `secret`
- `author`
- `mp_name`

### 4. 配置 IP 白名单

到微信公众号后台：
- 设置与开发 → 基本配置 → IP 白名单

查询当前公网 IP：

```bash
curl ifconfig.me
```

### 5. 测试链路

先测试 token 是否正常：

```bash
python3 - <<'PY'
import json, urllib.request, yaml
cfg = yaml.safe_load(open('toolkit/config.yaml', 'r', encoding='utf-8'))
appid = cfg['wechat']['appid']
secret = cfg['wechat']['secret']
url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
print(json.dumps(json.loads(urllib.request.urlopen(url, timeout=20).read()), ensure_ascii=False, indent=2))
PY
```

如果返回里有 `access_token`，说明 API 健康。

---

## 常用命令

### 新建草稿

```bash
~/.wechat-venv/bin/python3 toolkit/publish_article.py
```

### 更新已有草稿

```bash
~/.wechat-venv/bin/python3 toolkit/update_article.py
```

### 回拉远端草稿

```bash
~/.wechat-venv/bin/python3 toolkit/fetch_draft.py
```

### 调整正文 HTML 转换

```bash
~/.wechat-venv/bin/python3 toolkit/wechat_tech_converter.py
```

### 生成封面

```bash
~/.wechat-venv/bin/python3 toolkit/make_cover.py
```

---

## 推荐工作流

### 路线 A：从想法到发布
1. 用 `wechat-publish-workflow-skill` 记录素材
2. 整理出标题、hook、段落结构
3. 调整正文样式
4. 调整封面
5. 发布为新草稿

### 路线 B：已有草稿继续打磨
1. 回拉远端草稿
2. 对比修改点
3. 本地更新
4. 覆盖更新远端草稿

---

## 说明

当前采用的最佳方案是：

- **skill 管流程**
- **toolkit 管执行**

也就是：
- `wechat-publish-workflow-skill` 做“脑子”
- `toolkit/` 做“手脚”
