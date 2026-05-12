# Examples

## Example `.env`

```bash
WECHAT_MY_WECHAT_APP_ID=your_app_id
WECHAT_MY_WECHAT_APP_SECRET=your_app_secret
```

## Example `EXTEND.md`

```md
default_theme: studio-notes
default_color: blue
default_publish_method: api
default_author: Your Name
need_open_comment: 1
only_fans_can_comment: 0

accounts:
  - name: 我的公众号
    alias: my-wechat
    default: true
    default_publish_method: api
    default_author: Your Name
    need_open_comment: 1
    only_fans_can_comment: 0
```

## Example Token Check

```bash
python3 - <<'PY'
import json, urllib.request
appid='YOUR_APP_ID'
secret='YOUR_APP_SECRET'
url=f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
print(json.dumps(json.loads(urllib.request.urlopen(url, timeout=20).read()), ensure_ascii=False, indent=2))
PY
```

## Example Success Response

```json
{
  "access_token": "103_xxx",
  "expires_in": 7200
}
```

## Example Whitelist Failure

```json
{
  "errcode": 40164,
  "errmsg": "invalid ip 110.73.135.213 ..."
}
```

## Example Trigger Phrases

- `我要开始写公众号了`
- `这段经历先帮我记下来`
- `先别写，先积累素材`
- `把我们这次聊天慢慢整理成文章`

## Example Capture Summary

```md
主题：不是不喜欢技术，而是被不适合自己的工作方式耗尽了
经历：长期做企业项目，越来越偏离自己真正擅长和热爱的技术探索
情绪：疲惫、拧巴、被消耗
判断：问题不是技术热爱消失，而是工作方式出了问题
可转化方向：个人反思类公众号文章
```
