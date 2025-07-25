# Discord Bot Collection

## 📰 ニュースBot (news_bot.py)
自動ニュース配信とエコー機能を提供

### 機能
- **定期ニュース配信**
  - 朝06:00 - NHK主要ニュース
  - 昼12:00 - Yahoo!ニュース
  - 夜18:00 - Google News
- **エコー機能** - 特定チャンネルでメッセージをそのまま返信
- **リアクション応答** - 👍 に自動応答

### コマンド
- `/news_help` - 機能説明
- `/news_status` - 配信状態確認

### 起動方法
```bash
./run_news_bot.sh
# または
python3 news_bot.py
```

---

## 📝 ObsidianBot (obsidian_bot.py)
Discordメッセージを自動的にObsidian形式のデイリーノートに変換

### 機能
- **自動ノート作成** - 特定チャンネルの投稿を日付別ファイルに保存
- **テンプレート機能** - 一般的なデイリーノート形式を採用
- **ファイルダウンロード** - Discord経由で.mdファイルを取得

### コマンド
- `/obsidian_status` - 保存状態確認
- `/download_note [日付]` - ノートファイルダウンロード
- `/list_notes` - 保存済みノート一覧

### 起動方法
```bash
./run_obsidian_bot.sh  
# または
python3 obsidian_bot.py
```

---

## 🔧 設定

### 環境変数 (.env)
```
DISCORD_TOKEN=your_bot_token_here
OBSIDIAN_VAULT_PATH=/path/to/save/notes  # Obsidian用
```

### チャンネル設定
- ニュース配信: `1398171685613469746`
- エコー機能: `1397720382236135446`  
- Obsidian記録: `1398238810730664056`

### サーバー制限
- 対象サーバーID: `1397720381149806723`

---

## 🚀 デプロイ (Railway)

### ニュースBot
```bash
railway up --service news-bot
```

### ObsidianBot  
```bash
railway up --service obsidian-bot
```

---

## 📋 ファイル構成
```
├── news_bot.py                    # ニュース配信Bot ✅ ACTIVE
├── obsidian_bot.py                # ObsidianノートBot ✅ ACTIVE
├── requirements_news.txt          # ニュースBot依存関係
├── requirements_obsidian.txt      # ObsidianBot依存関係
├── run_news_bot.sh                # ニュースBot起動スクリプト
├── run_obsidian_bot.sh            # ObsidianBot起動スクリプト
├── archive/                       # アーカイブフォルダ
│   ├── bot_legacy_unified.py      # 旧統合版（レガシー）
│   └── requirements_legacy.txt    # 旧依存関係
└── .env                           # 環境変数
```

## 🔄 移行履歴

### 2025年7月25日 - 統合版から分離版への移行完了
- ✅ `bot.py` → `archive/bot_legacy_unified.py` に移動
- ✅ 機能を `news_bot.py` と `obsidian_bot.py` に分離
- ✅ セキュリティ対策を追加（入力検証、ファイルサイズ制限）
- ✅ 依存関係を最新化（aiohttp 3.12.x対応）

### 移行メリット
- 🚀 **独立運用**: 片方がダウンしても他方は動作継続
- 🔧 **保守性向上**: 機能別の修正・更新が容易
- 🛡️ **セキュリティ強化**: 入力検証とファイル制限を追加
- ⚡ **軽量化**: 必要な機能のみ読み込み

Updated 2025年 7月25日 金曜日 19時35分
