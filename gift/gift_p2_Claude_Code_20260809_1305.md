# Claude Codeでコードレビューを読み取り専用で自動化 - 実践テンプレート

## この動画で学んだこと
Claude Codeのサブエージェント機能を使い、`disallowedTools`を設定することで、コードを変更せず読み取り専用でレビューする専用エージェントを作成できます。

## すぐに使えるテンプレート

### 1. レビュー専用サブエージェントの設定ファイル

`.claude/agents/reviewer.md` を作成します：

```markdown
---
name: reviewer
description: コードレビュー専用エージェント。読み取り専用で動作し、コードの変更は行いません。
disallowedTools: Write, Edit
---

あなたはシニアコードレビュアーです。
以下の観点でコードをレビューし、改善点を提案してください。

## レビュー観点
1. **バグの可能性**: 論理エラー、境界値、null/undefinedチェック
2. **セキュリティ**: インジェクション、認証・認可の漏れ
3. **パフォーマンス**: 不要なループ、メモリリーク、N+1問題
4. **可読性**: 命名、コメント、複雑度
5. **テスト**: テストカバレッジ、エッジケース

## 出力形式
- 各指摘に重要度（🔴高 / 🟡中 / 🟢低）を付与
- ファイルパスと行番号を明記
- 具体的な改善案を提示
```

### 2. レビュー実行コマンド

```bash
# 特定のファイルをレビュー
claude --agent reviewer "src/app.ts をレビューしてください"

# 最近変更したファイルをレビュー
claude --agent reviewer "git diff --name-only HEAD~1 で変更されたファイルをレビュー"

# 特定ディレクトリ全体をレビュー
claude --agent reviewer "src/components/ ディレクトリのコードをレビュー"
```

### 3. プロジェクト全体のレビュースクリプト

`scripts/review.sh` を作成します：

```bash
#!/bin/bash

# コードレビュー自動化スクリプト
# 使用方法: ./scripts/review.sh [ファイルパス]

# レビュー対象のファイルを取得（引数があればそれを使用、なければ変更ファイル）
if [ -n "$1" ]; then
    TARGET="$1"
else
    # 直近のコミットで変更されたファイルを取得
    TARGET=$(git diff --name-only HEAD~1 | grep -E '\.(ts|js|py|rb|go)$' | tr '\n' ' ')
fi

if [ -z "$TARGET" ]; then
    echo "レビュー対象のファイルが見つかりません"
    exit 1
fi

echo "🔍 レビュー対象: $TARGET"
echo "----------------------------------------"

# Claude Codeでレビュー実行
claude --agent reviewer "以下のファイルをレビューしてください: $TARGET"

echo "----------------------------------------"
echo "✅ レビュー完了"
```

### 4. レビュー結果を保存するスクリプト

`scripts/review_with_output.sh` を作成します：

```bash
#!/bin/bash

# レビュー結果をファイルに保存するスクリプト
# 使用方法: ./scripts/review_with_output.sh [ファイルパス]

# タイムスタンプ付きの出力ファイル名を生成
OUTPUT_FILE="review_results_$(date +%Y%m%d_%H%M%S).md"

# レビュー対象のファイルを取得
if [ -n "$1" ]; then
    TARGET="$1"
else
    TARGET=$(git diff --name-only HEAD~1 | grep -E '\.(ts|js|py|rb|go)$' | tr '\n' ' ')
fi

echo "📝 レビュー結果を $OUTPUT_FILE に保存します"

# レビュー実行と結果保存
{
    echo "# コードレビュー結果"
    echo ""
    echo "## レビュー対象: $TARGET"
    echo ""
    echo "## レビュー日時: $(date)"
    echo ""
    echo "---"
    echo ""
    claude --agent reviewer "以下のファイルを詳細にレビューしてください: $TARGET"
} > "$OUTPUT_FILE"

echo "✅ レビュー結果を $OUTPUT_FILE に保存しました"
```

## 使い方

1. **設定ファイルの作成**: `.claude/agents/reviewer.md` を作成し、上記のテンプレートをコピー&ペーストします
2. **実行権限の付与**: `chmod +x scripts/review.sh scripts/review_with_output.sh` でスクリプトに実行権限を付与します
3. **レビュー実行**: 以下のいずれかの方法でレビューを実行します
   - 直接コマンド: `claude --agent reviewer "ファイル名をレビュー"`
   - スクリプト使用: `./scripts/review.sh src/app.ts`
   - 変更ファイル自動レビュー: `./scripts/review.sh`
4. **結果の確認**: レビュー結果は重要度付きで表示されます

## よくある質問

**Q: レビュー中にコードが変更されることはありますか？**
A: いいえ。`disallowedTools: Write, Edit` を設定しているため、レビューエージェントはファイルの読み取りと分析のみを行い、コードの変更や書き込みは一切行いません。

**Q: 複数のファイルを一度にレビューできますか？**
A: はい。スペース区切りで複数のファイルを指定できます。例: `claude --agent reviewer "src/app.ts src/utils.ts src/types.ts をレビュー"`

**Q: レビュー結果をチームで共有したい場合は？**
A: `scripts/review_with_output.sh` を使用すると、レビュー結果がMarkdownファイルとして保存されるため、PRのコメントやチームのドキュメントとして共有できます。

**Q: レビューの観点をカスタマイズできますか？**
A: はい。`.claude/agents/reviewer.md` の「レビュー観点」セクションを編集することで、プロジェクトの要件に合わせてカスタマイズできます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit