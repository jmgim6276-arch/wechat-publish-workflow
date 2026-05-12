#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${HOME}/.wechat-venv"

if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install -r "$ROOT/toolkit/requirements.txt"

if [ ! -f "$ROOT/toolkit/config.yaml" ]; then
  cp "$ROOT/toolkit/config.yaml.example" "$ROOT/toolkit/config.yaml"
  echo "已生成 $ROOT/toolkit/config.yaml，请先填写公众号凭据。"
else
  echo "config.yaml 已存在，跳过复制。"
fi

echo "初始化完成。下一步："
echo "1) 编辑 toolkit/config.yaml"
echo "2) 把当前公网 IP 加入公众号白名单"
echo "3) 运行 scripts/check_token.sh 测试 access_token"
