# clab-mcp-ipclos

Containerlab 上で構築した IP-CLOS 検証環境に、Nornir + Netmiko を利用した MCP Server を組み合わせる検証用リポジトリです。

詳細な内容や手順は、以下の記事を参照してください。

https://qiita.com/k-maki/items/b67a7e44545bce2ab369

## 概要

このリポジトリでは、Containerlab で構築したマルチベンダーの EVPN/VXLAN IP-CLOS 環境に対して、MCP Server 経由で複数機器の状態確認を行う構成を試しています。

Codex などの MCP クライアントから自然言語で指示することで、Nornir と Netmiko を利用して各ネットワーク機器へ接続し、show コマンドの実行や障害切り分けを行えるかを検証しています。
<img width="1062" height="669" alt="image" src="https://github.com/user-attachments/assets/3cb613be-62c7-4bc2-b8dd-c125e9785597" />


## 主な内容

- Containerlab による IP-CLOS ラボ環境
- マルチベンダー構成の EVPN/VXLAN 検証
- Nornir + Netmiko を利用した MCP Server
- Codex からの自然言語による状態確認
- 複数機器を対象にした BGP / EVPN / VXLAN などの確認
- 障害切り分けの検証

## 補足

このリポジトリは検証用です。  
構成内容、使い方、実行例などの詳細は Qiita 記事側にまとめています。

