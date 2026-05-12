# Setup and Whitelist

This file covers the real-world 公众号 API setup flow that was already tested in Tang's environment.

## Goal

Get these three things:

1. `AppID`
2. `AppSecret`
3. current公网IP added to the公众号后台 API whitelist

## Where to Find AppID and AppSecret

Reference notes:

`/Users/tang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Workshop/📓 睡前写-日记/2026年/4月/4月25日/4月25日.md`

Practical path:

1. Open `https://mp.weixin.qq.com/`
2. Log into the Official Account backend
3. Find the left-side menu entry related to 开发 / 开发接口管理
4. Follow the flow into the WeChat developer platform if needed
5. Locate:
   - `AppID`
   - `AppSecret`
   - `IP 白名单`

Notes:

- `AppID` can usually be copied directly
- `AppSecret` may need to be enabled or reset
- If reset, update the real config source immediately

## Where to Store Credentials

Preferred local storage in this environment:

`/Users/tang/.baoyu-skills/.env`

Example:

```bash
WECHAT_MY_WECHAT_APP_ID=your_app_id
WECHAT_MY_WECHAT_APP_SECRET=your_app_secret
```

The active account alias should match the config in:

`/Users/tang/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md`

## The Fastest Connectivity Test

```bash
python3 - <<'PY'
import json, urllib.request
appid='YOUR_APP_ID'
secret='YOUR_APP_SECRET'
url=f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
print(json.dumps(json.loads(urllib.request.urlopen(url, timeout=20).read()), ensure_ascii=False, indent=2))
PY
```

## Whitelist Troubleshooting

### Error: `40164 invalid ip`

Meaning:

- credentials may be correct
- current公网IP is not in the 公众号 API whitelist

Action:

1. read the IP shown in the error payload
2. add exactly that IP into the公众号后台白名单
3. save
4. retry token test

Important:

- the current公网IP can change between retries
- do not assume the previous IP is still valid
- if network conditions are unstable, keep older working IPs too

Example of a real error shape:

```json
{
  "errcode": 40164,
  "errmsg": "invalid ip 110.73.135.213 ..."
}
```

### Error: `40125 invalid appsecret`

Meaning:

- the script likely read the wrong secret
- or an old config file is still in use

Action:

1. inspect the script
2. confirm whether it reads `~/.baoyu-skills/.env` or `toolkit/config.yaml`
3. fix the actual source, not just the file you expect it to read

## Success Condition

Only call the account "connected" when the token request returns:

```json
{
  "access_token": "...",
  "expires_in": 7200
}
```
