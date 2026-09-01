# SOCKS5 MVP + AWS us4 出口 IP 池采样报告

采样时间: 2026-09-01 05:29–05:31 UTC  
主机: `cursor`  
gost: 2.11.5 (go1.19.2 linux/amd64)

## SOCKS5 连接串

```
socks5://dev_17647e:f2BPDUMlhzHOoLBMVgJyd5eq@127.0.0.1:1080
```

- user: `dev_17647e`
- pass: `f2BPDUMlhzHOoLBMVgJyd5eq`
- bind: `127.0.0.1:1080` (仅本机, 强制 auth)
- 二进制: `/workspace/proxy/gost`
- 凭据文件: `/workspace/proxy/.credentials` (mode 600)

Cursor Desktop 端口自动转发后, Windows 本机使用同一连接串即可。

## gost 进程

- pid: `1655`
- 启动命令行:

```
./gost -L socks5://dev_17647e:f2BPDUMlhzHOoLBMVgJyd5eq@127.0.0.1:1080
```

- `ps -p 1655 -o pid,stat,cmd`:

```
    PID STAT CMD
   1655 Sl   ./gost -L socks5://dev_17647e:f2BPDUMlhzHOoLBMVgJyd5eq@127.0.0.1:1080
```

### gost.log 头 20 行

```
2026/09/01 05:29:24 route.go:695: socks5://127.0.0.1:1080 on 127.0.0.1:1080
2026/09/01 05:30:00 socks.go:889: [socks5] 127.0.0.1:32980 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:941: [route] 127.0.0.1:32980 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:976: [socks5] 127.0.0.1:32980 <-> checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:978: [socks5] 127.0.0.1:32980 >-< checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:889: [socks5] 127.0.0.1:32984 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:941: [route] 127.0.0.1:32984 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:00 socks.go:976: [socks5] 127.0.0.1:32984 <-> checkip.amazonaws.com:443
2026/09/01 05:30:01 socks.go:978: [socks5] 127.0.0.1:32984 >-< checkip.amazonaws.com:443
2026/09/01 05:30:01 socks.go:889: [socks5] 127.0.0.1:32988 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:01 socks.go:941: [route] 127.0.0.1:32988 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:01 socks.go:976: [socks5] 127.0.0.1:32988 <-> checkip.amazonaws.com:443
2026/09/01 05:30:01 socks.go:978: [socks5] 127.0.0.1:32988 >-< checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:889: [socks5] 127.0.0.1:32994 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:941: [route] 127.0.0.1:32994 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:976: [socks5] 127.0.0.1:32994 <-> checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:978: [socks5] 127.0.0.1:32994 >-< checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:889: [socks5] 127.0.0.1:33008 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:941: [route] 127.0.0.1:33008 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:30:02 socks.go:976: [socks5] 127.0.0.1:33008 <-> checkip.amazonaws.com:443
```

## ss -tlnp 中 1080 那一行 (原样)

```
LISTEN 0      4096       127.0.0.1:1080       0.0.0.0:*    users:(("gost",pid=1655,fd=8))     
```

## 新连接采样 (Step 4)

- 采样次数: 60 / 60 成功 (无超时、无空行)
- 观测 unique IP 数: **8**
- 完成判据: ≥30 条结果且 ≥5 个不同 IP — **通过**

### 频次分布 (`07-ip-freq.txt` 全文)

```
     12 44.239.176.212
     10 52.13.17.46
     10 35.167.27.154
      8 52.40.48.127
      7 54.201.20.43
      6 50.112.242.221
      4 44.236.205.197
      3 52.34.217.149
```

### 60 次新连接原始结果 (`06-ip-fresh-connections.txt` 全文)

```
1 44.239.176.212
2 52.40.48.127
3 52.40.48.127
4 54.201.20.43
5 52.34.217.149
6 52.13.17.46
7 54.201.20.43
8 35.167.27.154
9 50.112.242.221
10 52.40.48.127
11 52.34.217.149
12 52.13.17.46
13 35.167.27.154
14 44.239.176.212
15 50.112.242.221
16 35.167.27.154
17 52.13.17.46
18 44.239.176.212
19 35.167.27.154
20 44.239.176.212
21 50.112.242.221
22 54.201.20.43
23 44.236.205.197
24 44.236.205.197
25 52.34.217.149
26 52.13.17.46
27 52.40.48.127
28 44.239.176.212
29 44.239.176.212
30 52.13.17.46
31 52.40.48.127
32 35.167.27.154
33 44.236.205.197
34 44.239.176.212
35 52.40.48.127
36 35.167.27.154
37 44.239.176.212
38 50.112.242.221
39 52.13.17.46
40 52.13.17.46
41 54.201.20.43
42 54.201.20.43
43 44.239.176.212
44 44.239.176.212
45 50.112.242.221
46 52.13.17.46
47 35.167.27.154
48 54.201.20.43
49 50.112.242.221
50 35.167.27.154
51 52.40.48.127
52 44.239.176.212
53 52.40.48.127
54 35.167.27.154
55 44.236.205.197
56 52.13.17.46
57 54.201.20.43
58 35.167.27.154
59 44.239.176.212
60 52.13.17.46
```

## 每个 IP 的 ip-api 分类 (Step 6, 全部行)

| ip | country | city | asname | hosting | proxy | mobile |
|---|---|---|---|---|---|---|
| 35.167.27.154 | United States | Portland | AMAZON-02 | true | false | false |
| 44.236.205.197 | United States | Portland | AMAZON-02 | true | false | false |
| 44.239.176.212 | United States | Portland | AMAZON-02 | true | false | false |
| 50.112.242.221 | United States | Portland | AMAZON-02 | true | false | false |
| 52.13.17.46 | United States | Portland | AMAZON-02 | true | false | false |
| 52.34.217.149 | United States | Portland | AMAZON-02 | true | false | false |
| 52.40.48.127 | United States | Portland | AMAZON-02 | true | false | false |
| 54.201.20.43 | United States | Portland | AMAZON-02 | true | false | false |

补充字段 (8 个 IP 完全一致):

- regionName: Oregon
- isp: Amazon.com, Inc.
- org: AWS EC2 (us-west-2)
- as: AS16509 Amazon.com, Inc.

结论: 全部是 AWS EC2 us-west-2 托管出口 (`hosting=true`), 不是住宅/移动/公开代理标签 (`proxy=false`, `mobile=false`)。

## 观测集是否 ⊂ cloudAgents.us4 (Step 7)

`11-pool-coverage.txt` 全文:

```
observed unique IPs: 8
us4 pool total    : 32
observed⊂ us4    : True
observed - us4    : set()  # should be empty
us4 not yet seen  : ['32.185.18.216', '34.215.42.124', '34.223.75.203', '35.162.90.105', '44.225.28.243', '44.226.243.231', '44.228.224.16', '44.229.131.104', '44.229.62.106', '44.230.163.89', '44.233.218.155', '44.239.171.255', '44.239.53.183', '44.250.14.191', '50.112.57.248', '52.11.201.85', '52.25.246.27', '52.26.62.193', '52.40.244.0', '52.88.153.61', '54.187.34.250', '54.201.15.58', '54.201.2.165', '54.203.101.43']
```

- 观测 8 个 IP **全部属于** 官方 `cloudAgents.us4` 32 个 `/32`
- `observed - us4` 为空
- 尚未采到的 us4 IP (24 个):
  - 32.185.18.216
  - 34.215.42.124
  - 34.223.75.203
  - 35.162.90.105
  - 44.225.28.243
  - 44.226.243.231
  - 44.228.224.16
  - 44.229.131.104
  - 44.229.62.106
  - 44.230.163.89
  - 44.233.218.155
  - 44.239.171.255
  - 44.239.53.183
  - 44.250.14.191
  - 50.112.57.248
  - 52.11.201.85
  - 52.25.246.27
  - 52.26.62.193
  - 52.40.244.0
  - 52.88.153.61
  - 54.187.34.250
  - 54.201.15.58
  - 54.201.2.165
  - 54.203.101.43

覆盖率: 8/32 = 25%。新 TCP 连接会在池内轮换, 60 次不足以铺满 32 个出口。

## keep-alive 单连接 20 次 IP (Step 5, 全部行)

```
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
52.34.217.149
```

20 行全部相同 (`52.34.217.149`), 证明同一条 TCP 连接出口稳定, 不在连接内轮换。

## UDP STUN SNAT (Step 8, 全部行)

本步走 Pod 本机 UDP (不经 gost SOCKS5 TCP):

```
stun.l.google.com -> 44.236.205.197:42984
stun.l.google.com -> 52.13.17.46:55705
stun.l.google.com -> 52.13.17.46:13779
stun.cloudflare.com err: timed out
stun.cloudflare.com err: timed out
stun.cloudflare.com err: timed out
stun1.l.google.com -> 44.236.205.197:2589
stun1.l.google.com -> 54.201.20.43:28150
stun1.l.google.com -> 44.236.205.197:12976
```

- Google STUN 6/6 成功, 出口 IP 均落在已观测的 us4 子集, 端口每次不同
- 同一 host 连续 3 次也会换 IP/端口 (UDP 出口同样走轮换池)
- Cloudflare STUN (`stun.cloudflare.com:19302`) 三次全部 timed out

## 异常

1. **`ss` 最初不存在**: 镜像未装 `iproute2`。gost 已在 `127.0.0.1:1080` 监听 (当时用 `netstat -tlnp` / `lsof -p 1655` 确认)。已 `sudo apt-get install -y iproute2` (iproute2-6.1.0), 之后 `ss -tlnp` 看到 `127.0.0.1:1080 LISTEN`。未改 environment.json。
2. **`stun.cloudflare.com` 三次 UDP timeout** (4s)。Google STUN 正常, 判定为该 STUN 目标不可达/被滤, 不是本机 UDP 全挂。
3. **gost 启动瞬间日志只有 1 行**: `05-gost-startup.txt` 捕获于 sleep 2 之后、采样之前, 仅 `route.go:695: socks5://127.0.0.1:1080 on 127.0.0.1:1080`。流量进入后日志才增长; 上头 20 行取自采样后的 `02-gost.log`。
4. **无** checkip.amazonaws.com 超时/失败 (60/60 + keepalive 20/20)。
5. **无** gost 启动错误。
6. **无** ip-api.com 429/403 (8/8 成功)。
7. 60 次新连接只覆盖 8/32 us4 IP, 不是错误, 是采样宽度不足。

## Pod 内网 IP 与 hostname

```
hostname: cursor
ip a show eth0 | grep inet:
    inet 172.30.0.2/24 brd 172.30.0.255 scope global eth0
    inet6 fe80::802b:38ff:fe3d:bcd0/64 scope link
```

## 完成判据

| 项 | 结果 |
|---|---|
| ss 显示 1080 LISTEN | 通过 (`127.0.0.1:1080`, pid=1655) |
| Step 4 ≥30 条 IP 且 ≥5 个不同 IP | 通过 (60 条, 8 个 unique) |
| Step 6/7 输出完整 | 通过 |
| REPORT.md 已生成 | 通过 |

---

## 附录: 全部原始产物 (单文件归档)

### A. `01-gost-version.txt`

```
gost 2.11.5 (go1.19.2 linux/amd64)
```

### B. `03-listen.txt` (`ss -tlnp | grep -E '1080|LISTEN'` 全文)

```
LISTEN 0      4096       127.0.0.1:1080       0.0.0.0:*    users:(("gost",pid=1655,fd=8))     
LISTEN 0      5            0.0.0.0:2375       0.0.0.0:*                                       
LISTEN 0      128          0.0.0.0:50052      0.0.0.0:*                                       
LISTEN 0      100          0.0.0.0:26058      0.0.0.0:*    users:(("python3",pid=1062,fd=3))  
LISTEN 0      128          0.0.0.0:26500      0.0.0.0:*                                       
LISTEN 0      5          127.0.0.1:5901       0.0.0.0:*    users:(("Xtigervnc",pid=860,fd=9)) 
LISTEN 0      5              [::1]:5901          [::]:*    users:(("Xtigervnc",pid=860,fd=10))
LISTEN 0      511                *:26053            *:*    users:(("node",pid=278,fd=21))     
LISTEN 0      511                *:26054            *:*    users:(("node",pid=278,fd=22))     
```

### C. `04-process.txt`

```
    PID STAT CMD
   1655 Sl   ./gost -L socks5://dev_17647e:f2BPDUMlhzHOoLBMVgJyd5eq@127.0.0.1:1080
```

### D. `05-gost-startup.txt` (启动瞬间, 采样前)

```
2026/09/01 05:29:24 route.go:695: socks5://127.0.0.1:1080 on 127.0.0.1:1080
```

### E. `09-ip-details.jsonl` 全文

```
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"35.167.27.154"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"44.236.205.197"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"44.239.176.212"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"50.112.242.221"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"52.13.17.46"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"52.34.217.149"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"52.40.48.127"}
{"country":"United States","regionName":"Oregon","city":"Portland","isp":"Amazon.com, Inc.","org":"AWS EC2 (us-west-2)","as":"AS16509 Amazon.com, Inc.","asname":"AMAZON-02","mobile":false,"proxy":false,"hosting":true,"query":"54.201.20.43"}
```

### F. 官方 `cloudAgents.us4` 32 个 `/32` (摘自 `10-cursor-ips.json`)

```
32.185.18.216/32
34.215.42.124/32
34.223.75.203/32
35.162.90.105/32
35.167.27.154/32
44.225.28.243/32
44.226.243.231/32
44.228.224.16/32
44.229.62.106/32
44.229.131.104/32
44.230.163.89/32
44.233.218.155/32
44.236.205.197/32
44.239.53.183/32
44.239.171.255/32
44.239.176.212/32
44.250.14.191/32
50.112.57.248/32
50.112.242.221/32
52.11.201.85/32
52.13.17.46/32
52.25.246.27/32
52.26.62.193/32
52.34.217.149/32
52.40.48.127/32
52.40.244.0/32
52.88.153.61/32
54.187.34.250/32
54.201.2.165/32
54.201.15.58/32
54.201.20.43/32
54.203.101.43/32
```

源文件: https://cursor.com/docs/ips.json (`version: 1`, `modified: 2026-05-29T19:43:24.653Z`)

### G. `.credentials`

```
USER=dev_17647e
PASS=f2BPDUMlhzHOoLBMVgJyd5eq
```
