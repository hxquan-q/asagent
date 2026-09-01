# SOCKS5 代理部署与 us4 IP 池采样报告

生成时间: 2026-09-01 UTC

## 1. SOCKS5 连接信息

```
socks5://dev_17b5b1:H8BFO4Yw31oGA7H349FXYRc2@127.0.0.1:1080
```

| 字段 | 值 |
|------|-----|
| User | `dev_17b5b1` |
| Pass | `H8BFO4Yw31oGA7H349FXYRc2` |
| Host | `127.0.0.1` |
| Port | `1080` |

> Cursor Desktop 端口转发会将 Pod 内 `127.0.0.1:1080` 暴露到 Windows 本机。

## 2. gost 进程

| 项 | 值 |
|----|-----|
| PID | `2856` |
| 版本 | gost 2.11.5 (go1.19.2 linux/amd64) |
| 启动命令 | `./gost -L "socks5://dev_17b5b1:H8BFO4Yw31oGA7H349FXYRc2@127.0.0.1:1080"` |
| PID 文件 | `/workspace/proxy/gost.pid` |
| 日志 | `/workspace/proxy/report/02-gost.log` |

### gost.log 头 20 行

```
2026/09/01 05:22:35 route.go:695: socks5://127.0.0.1:1080 on 127.0.0.1:1080
2026/09/01 05:22:57 socks.go:889: [socks5] 127.0.0.1:60730 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:941: [route] 127.0.0.1:60730 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:976: [socks5] 127.0.0.1:60730 <-> checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:978: [socks5] 127.0.0.1:60730 >-< checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:889: [socks5] 127.0.0.1:60742 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:941: [route] 127.0.0.1:60742 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:57 socks.go:976: [socks5] 127.0.0.1:60742 <-> checkip.amazonaws.com:443
2026/09/01 05:22:58 socks.go:978: [socks5] 127.0.0.1:60742 >-< checkip.amazonaws.com:443
2026/09/01 05:22:58 socks.go:889: [socks5] 127.0.0.1:33506 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:58 socks.go:941: [route] 127.0.0.1:33506 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:58 socks.go:976: [socks5] 127.0.0.1:33506 <-> checkip.amazonaws.com:443
2026/09/01 05:22:58 socks.go:978: [socks5] 127.0.0.1:33506 >-< checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:889: [socks5] 127.0.0.1:33510 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:941: [route] 127.0.0.1:33510 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:976: [socks5] 127.0.0.1:33510 <-> checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:978: [socks5] 127.0.0.1:33510 >-< checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:889: [socks5] 127.0.0.1:33524 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:941: [route] 127.0.0.1:33524 -> socks5://127.0.0.1:1080 -> checkip.amazonaws.com:443
2026/09/01 05:22:59 socks.go:976: [socks5] 127.0.0.1:33524 <-> checkip.amazonaws.com:443
```

## 3. 监听状态

`ss -tlnp` 中 1080 那一行原样:

```
LISTEN 0      4096       127.0.0.1:1080       0.0.0.0:*    users:(("gost",pid=2856,fd=8))      
```

### 完整 `ss -tlnp | grep -E '1080|LISTEN'` 输出

```
LISTEN 0      4096       127.0.0.1:1080       0.0.0.0:*    users:(("gost",pid=2856,fd=8))      
LISTEN 0      5          127.0.0.1:5901       0.0.0.0:*    users:(("Xtigervnc",pid=2080,fd=9)) 
LISTEN 0      5            0.0.0.0:2375       0.0.0.0:*                                        
LISTEN 0      128          0.0.0.0:50052      0.0.0.0:*                                        
LISTEN 0      128          0.0.0.0:26500      0.0.0.0:*                                        
LISTEN 0      100          0.0.0.0:26058      0.0.0.0:*    users:(("python3",pid=2305,fd=3))   
LISTEN 0      5              [::1]:5901          [::]:*    users:(("Xtigervnc",pid=2080,fd=10))
LISTEN 0      511                *:26054            *:*    users:(("node",pid=1502,fd=22))     
LISTEN 0      511                *:26053            *:*    users:(("node",pid=1502,fd=21))     
```

### 进程信息

```
PID STAT CMD
   2856 Sl   ./gost -L socks5://dev_17b5b1:H8BFO4Yw31oGA7H349FXYRc2@127.0.0.1:1080
```

## 4. IP 池采样 — 新连接 (60 次)

### 4.1 原始采样 (06-ip-fresh-connections.txt)

```
1 44.250.14.191
2 44.239.171.255
3 44.229.131.104
4 34.215.42.124
5 35.162.90.105
6 44.229.131.104
7 44.239.171.255
8 34.215.42.124
9 50.112.57.248
10 50.112.57.248
11 44.250.14.191
12 44.230.163.89
13 50.112.57.248
14 34.215.42.124
15 44.250.14.191
16 44.229.131.104
17 44.239.171.255
18 44.229.131.104
19 50.112.57.248
20 44.239.53.183
21 44.250.14.191
22 35.162.90.105
23 44.250.14.191
24 44.230.163.89
25 44.239.53.183
26 50.112.57.248
27 44.239.171.255
28 44.239.53.183
29 44.230.163.89
30 34.215.42.124
31 34.215.42.124
32 35.162.90.105
33 44.239.53.183
34 44.239.171.255
35 44.230.163.89
36 35.162.90.105
37 44.230.163.89
38 44.250.14.191
39 44.239.171.255
40 34.215.42.124
41 35.162.90.105
42 34.215.42.124
43 44.250.14.191
44 34.215.42.124
45 44.250.14.191
46 44.250.14.191
47 44.239.171.255
48 44.250.14.191
49 44.229.131.104
50 35.162.90.105
51 44.229.131.104
52 50.112.57.248
53 44.250.14.191
54 44.230.163.89
55 35.162.90.105
56 44.239.53.183
57 44.250.14.191
58 44.239.171.255
59 44.239.53.183
60 34.215.42.124
```

### 4.2 频次分布 (07-ip-freq.txt)

```
12 44.250.14.191
      9 34.215.42.124
      8 44.239.171.255
      7 35.162.90.105
      6 50.112.57.248
      6 44.239.53.183
      6 44.230.163.89
      6 44.229.131.104
```

- 采样总数: 60
- 唯一 IP 数: 8
- 判定: 通过 (≥ 5 个不同 IP)

## 5. IP 类型 / ASN 分析 (ip-api.com)

| IP | Country | City | AS Name | Hosting | Proxy | Mobile |
|----|---------|------|---------|---------|-------|--------|
| 34.215.42.124 | United States | Portland | AMAZON-02 | True | False | False |
| 35.162.90.105 | United States | Portland | AMAZON-02 | True | False | False |
| 44.229.131.104 | United States | Portland | AMAZON-02 | True | False | False |
| 44.230.163.89 | United States | Portland | AMAZON-02 | True | False | False |
| 44.239.171.255 | United States | Portland | AMAZON-02 | True | False | False |
| 44.239.53.183 | United States | Portland | AMAZON-02 | True | False | False |
| 44.250.14.191 | United States | Portland | AMAZON-02 | True | False | False |
| 50.112.57.248 | United States | Portland | AMAZON-02 | True | False | False |

## 6. cloudAgents.us4 官方池交叉验证

```
observed unique IPs: 8
us4 pool total    : 32
observed⊂ us4    : True
observed - us4    : set()  # should be empty
us4 not yet seen  : ['32.185.18.216', '34.223.75.203', '35.167.27.154', '44.225.28.243', '44.226.243.231', '44.228.224.16', '44.229.62.106', '44.233.218.155', '44.236.205.197', '44.239.176.212', '50.112.242.221', '52.11.201.85', '52.13.17.46', '52.25.246.27', '52.26.62.193', '52.34.217.149', '52.40.244.0', '52.40.48.127', '52.88.153.61', '54.187.34.250', '54.201.15.58', '54.201.2.165', '54.201.20.43', '54.203.101.43']
```

## 7. Keep-Alive 单连接 20 次采样

```
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
44.250.14.191
```

结论: 20 行全部为 `44.250.14.191`，同 TCP 连接出口 IP 稳定。

## 8. UDP STUN 出口 SNAT (Pod 本机 UDP，非 SOCKS5)

```
stun.l.google.com -> 50.112.57.248:15122
stun.l.google.com -> 35.162.90.105:20073
stun.l.google.com -> 34.215.42.124:57374
stun.cloudflare.com err: timed out
stun.cloudflare.com err: timed out
stun.cloudflare.com err: timed out
stun1.l.google.com -> 44.230.163.89:36292
stun1.l.google.com -> 44.229.131.104:9171
stun1.l.google.com -> 44.230.163.89:6444
```

结论: UDP 出口同样走 us4 池轮换（观测到的 IP 均在采样 TCP 集合内）；`stun.cloudflare.com` 三次超时。

## 9. 异常与备注

- 镜像默认无 `ss`/`ip`（iproute2 未预装）。已 `apt-get install iproute2` 后按原命令复验；`ss` 确认 `127.0.0.1:1080 LISTEN`（gost pid=2856）。
- UDP STUN: stun.cloudflare.com err: timed out
- UDP STUN: stun.cloudflare.com err: timed out
- UDP STUN: stun.cloudflare.com err: timed out
- 未改 environment.json，未装 systemd 服务，未对任何进程 pkill/killall。

## 10. Pod 环境

`ip a show eth0 | grep inet` 原样:

```
    inet 172.30.0.2/24 brd 172.30.0.255 scope global eth0
    inet6 fe80::802b:38ff:fe3d:bcd0/64 scope link 
```

| 项 | 值 |
|----|-----|
| hostname | `cursor` |
| eth0 inet | `172.30.0.2/24` |
| hostname -I | `172.30.0.2 172.17.0.1` |
| eth0 MAC | `82:2b:38:3d:bc:d0` |
| gost 二进制 | `/workspace/proxy/gost` |
| 凭证文件 | `/workspace/proxy/.credentials` (chmod 600) |

## 11. 完成判据检查

| 判据 | 结果 |
|------|------|
| 1080 LISTEN | ✅ `ss` 显示 `127.0.0.1:1080` LISTEN (PID 2856) |
| Step 4 ≥ 30 条结果, ≥ 5 IP | ✅ 60 条, 8 个唯一 IP |
| Step 6/7 完整 | ✅ |
| REPORT.md 生成 | ✅ |
