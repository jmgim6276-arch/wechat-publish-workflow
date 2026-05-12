#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import json, urllib.request, yaml
cfg = yaml.safe_load(open('toolkit/config.yaml', 'r', encoding='utf-8'))
appid = cfg['wechat']['appid']
secret = cfg['wechat']['secret']
url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
print(json.dumps(json.loads(urllib.request.urlopen(url, timeout=20).read()), ensure_ascii=False, indent=2))
PY
