# koyamaYT-rag-x2

小山さん（りゅう先生）としての文体・トーンで、**RAG（`小山さん/` と `insights/`）と X トレンド**を組み合わせ、**長文 X 記事** または **YouTube 台本（30分＋Shorts3本）** を生成する [Claude Code](https://claude.ai/claude-code) 用ワークスペースです。

**GitHub（Public）:** [https://github.com/ai776/koyamaYT-rag-x2](https://github.com/ai776/koyamaYT-rag-x2)

| 内容 | 正本 |
|------|------|
| X 長文記事 | `.claude/skills/koyama-x-post/SKILL.md` |
| YouTube 台本 | `.claude/skills/koyama-yt-script/SKILL.md` |
| RAG の考え方 | `.claude/skills/_shared/rag-usage-policy.md` |
| テーマ別の仕訳・優先ファイル | `insights/_routing.md` |

## ワークフロー概要

1. テーマ受け取り → X リサーチ ON/OFF、X API の確認  
2. X でリサーチ（任意）  
3. 構成の整理  
4. **RAG** … 先に **`insights/_routing.md`** で仕訳し、そこに書かれた `小山さん/` または `insights/` の優先ファイルを読む。足りなければ両方を grep  
5. 生成  
   - X 記事 → `articles/`（`YYMMDD_スラッグ.md`）  
   - 台本 → `scripts/`（`YYMMDD_スラッグ_yt.md`）  

## プロジェクト構成

```
koyamaYT-rag-x2/
├── README.md
├── articles/                 # 生成済み X 長文（Markdown）
├── scripts/                  # 生成済み YouTube 台本（Markdown）
├── insights/
│   ├── _routing.md           # RAG 仕訳インデックス（grep より先に読む）
│   ├── *_analysis.txt        # 補助コーパス
│   └── video_prompt/         # YouTube 向けプロンプト置き場
├── 小山さん/
│   ├── *_analysis.txt        # 主コーパス（分析メモ）
│   └── *_analytics.txt       # 同上（analytics 系ファイル）
├── tools/
│   ├── rag_smoke_test.py     # `_routing.md` 周りのスモークテスト
│   └── yt_to_tts.py          # 台本 MD → TTS 用クリーンテキスト（SKILL 参照）
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
| 元ファイル | `insights/`・`小山さん/` の移動・コピー・退避はしない（Read / Grep の参照のみ） |
| 履歴 | **使用履歴ログ・`_used`・クールダウンは持たない**（`rag-usage-policy.md` 参照） |

新規 `*_analysis.txt` を増やしたら、**`insights/_routing.md` にだけ**カテゴリ・キーワード・優先ファイルを追記すればよいです。

## 必要な環境

- [Claude Code](https://claude.ai/claude-code)
- X リサーチ用にインターネット接続  
- スモークテスト・TTS 変換: **Python 3**（標準ライブラリ中心。`yt_to_tts.py` は `pathlib` / `re` のみ）

## X API（任意）

未設定でも WebSearch／Nitter 等で動作します。Bearer Token と Pay-Per-Use は [X Developer](https://developer.x.com) / [console.x.com](https://console.x.com) の公式手順に従ってください。

## 使い方の例

- 「〜で小山さんの X 長文記事を」→ `koyama-x-post` を起動  
- 「〜の YouTube 台本を」→ `koyama-yt-script` を起動  

## RAG スモークテスト

`insights/_routing.md` のカテゴリ、優先ファイル参照、複合テーマを含む代表テーマの仕訳を確認できます。

```bash
python3 tools/rag_smoke_test.py
python3 tools/rag_smoke_test.py --topic '相席寿司屋さんは、なぜ伸びているのか？'
```

## 台本 → TTS 用テキスト

`.claude/skills/koyama-yt-script/SKILL.md` に合わせ、`scripts/` の台本から演出キュー等を除いた読み上げ用 Markdown を `scripts_tts/` に出力します。

```bash
python3 tools/yt_to_tts.py scripts/260417_greek-yogurt-guilt-free-trend_yt.md
python3 tools/yt_to_tts.py --all
```

## 公開・ライセンス

本リポジトリは GitHub 上で **Public** として公開しています。掲載テキスト・スキル定義などの再利用・再配布が必要な場合は、権利者の許諾や各コンテンツの取り扱いをご自身で確認してください。
