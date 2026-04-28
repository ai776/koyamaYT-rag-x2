# koyama-rag-x

小山さん（りゅう先生）としての文体・トーンで、**RAG（`小山さん/` と `insights/`）と X トレンド**を組み合わせ、**長文 X 記事** または **YouTube 台本（30分＋Shorts3本）** を生成する [Claude Code](https://claude.ai/claude-code) 用プロジェクトです。

| 内容 | 正本 |
|------|------|
| X 長文記事 | `.claude/skills/koyama-x-post/SKILL.md` |
| YouTube 台本 | `.claude/skills/koyama-yt-script/SKILL.md` |
| RAG の考え方 | `.claude/skills/_shared/rag-usage-policy.md` |

## ワークフロー概要

1. テーマ受け取り → X リサーチ ON/OFF、X API の確認  
2. X でリサーチ（任意）  
3. 構成の整理  
4. **RAG** … 先に **`insights/_routing.md`** で仕訳し、そこに書かれた `小山さん/` または `insights/` の優先ファイルを読む。足りなければ両方を grep  
5. 生成 → X 記事は `articles/`、台本は `scripts/`  

## プロジェクト構成

```
koyama-rag-x/
├── README.md
├── articles/
├── scripts/
├── insights/
│   ├── _routing.md
│   └── video_prompt/
├── 小山さん/
└── .claude/skills/
    ├── _shared/rag-usage-policy.md
    ├── koyama-x-post/SKILL.md
    └── koyama-yt-script/SKILL.md
```

## データ運用の要点

| 観点 | ルール |
|------|--------|
| 仕訳 | **grep より先に `insights/_routing.md`** |
| 取得 | 1 テーマあたり **広めに 5〜10 ファイル程度** |
| 反映 | X:**1〜2 件** / YT本編:**2〜3 件**。Shorts は本編事例の別角度 |
| 元ファイル | `insights/`・`小山さん/` は移動・削除しない |
| 履歴 | **`_used` やログは持たない** |

新規 `*_analysis.txt` を追加したら、このリポジトリの **`_routing.md` にだけ**カテゴリ・キーワード・優先ファイルを追記すればよいです。

## 必要な環境

- [Claude Code](https://claude.ai/claude-code)
- X リサーチ用にインターネット接続  

## X API（任意）

未設定でも WebSearch／Nitter 等で動作します。Bearer Token と Pay-Per-Use は [X Developer](https://developer.x.com) / [console.x.com](https://console.x.com) の公式手順に従ってください。

## 使い方の例

- 「〜で小山さんの X 長文記事を」→ `koyama-x-post` を起動  
- 「〜の YouTube 台本を」→ `koyama-yt-script` を起動  

## RAGスモークテスト

`insights/_routing.md` のカテゴリ、優先ファイル参照、複合テーマを含む代表テーマの仕訳を確認できます。

```bash
python3 tools/rag_smoke_test.py
python3 tools/rag_smoke_test.py --topic '相席寿司屋さんは、なぜ伸びているのか？'
```

## ライセンス

Private - All Rights Reserved
