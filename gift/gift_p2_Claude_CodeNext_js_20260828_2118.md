# Claude Codeの生成機能でNext.jsのサーバーコンポーネントが自動生成された - 実践テンプレート

## この動画で学んだこと
この動画では、AIアシスタント「Claude Code」を活用して、Next.jsのApp Routerにおけるサーバーコンポーネントを効率的に自動生成する方法を学びました。特に、データ取得の具体的な要件と`fetch` APIの`revalidate`オプションを用いたキャッシュ戦略をプロンプトで指示することが重要であると示されています。

## すぐに使えるテンプレート

ここでは、Claude Codeに与えるプロンプトと、それによって生成されるであろうNext.jsのサーバーコンポーネントのコード例を提供します。

### Claude Codeへ渡すプロンプト例

Next.jsのApp Routerにおいて、ブログ記事のリストを表示するサーバーコンポーネントを生成してください。

要件は以下の通りです。
1.  データは`https://jsonplaceholder.typicode.com/posts`から取得します。
2.  各記事の`id`と`title`を表示してください。
3.  `fetch` APIのキャッシュ戦略として、データが1時間（3600秒）ごとに再検証されるように設定してください。
4.  データ取得中のローディング状態と、データ取得失敗時のエラー表示を考慮してください。
5.  コードはTypeScriptを使用してください。
### 生成されるNext.jsサーバーコンポーネントのコード例 (`app/posts/page.tsx`)

// app/posts/page.tsx
import React, { Suspense } from 'react';

// 取得する記事データの型定義
interface Post {
  userId: number;
  id: number;
  title: string;
  body: string;
}

// データを取得する非同期関数
async function getPosts(): Promise<Post[]> {
  try {
    // fetch APIを使用してデータを取得。
    // next.revalidateオプションでキャッシュ戦略を定義。
    // ここでは3600秒（1時間）ごとにデータを再検証する設定。
    const res = await fetch('https://jsonplaceholder.typicode.com/posts', {
      next: { revalidate: 3600 }, // 1時間ごとにキャッシュを再検証
    });

    // レスポンスが正常でなければエラーをスロー
    if (!res.ok) {
      throw new Error(`Failed to fetch posts: ${res.status} ${res.statusText}`);
    }

    return res.json();
  } catch (error) {
    console.error('Error fetching posts:', error);
    // エラー発生時は空の配列を返すか、エラーを再スローすることも可能
    throw new Error('Failed to retrieve blog posts.');
  }
}

// サーバーコンポーネント
export default async function PostsPage() {
  let posts: Post[] = [];
  let error: string | null = null;

  try {
    posts = await getPosts();
  } catch (err: any) {
    error = err.message;
  }

  // エラーが発生した場合のUI
  if (error) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">ブログ記事</h1>
        <p className="text-red-500">エラー: {error}</p>
        <p>データの取得に失敗しました。時間をおいて再度お試しください。</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">ブログ記事</h1>
      {/* データの取得中はSuspenseでローディング表示することも可能ですが、
          サーバーコンポーネントの場合、通常はデータ取得完了後にレンダリングされます。
          より複雑なネストされたコンポーネントでSuspenseが役立ちます。 */}
      <Suspense fallback={<div>記事を読み込み中...</div>}>
        <ul className="space-y-4">
          {posts.map((post) => (
            <li key={post.id} className="border p-4 rounded-md shadow-sm">
              <h2 className="text-xl font-semibold mb-2">{post.title}</h2>
              <p className="text-gray-600">ID: {post.id}</p>
            </li>
          ))}
        </ul>
      </Suspense>
    </div>
  );
}
## 使い方
1.  **プロンプトをClaude Codeに貼り付ける**: 上記の「Claude Codeへ渡すプロンプト例」をClaude CodeなどのAIアシスタントにコピー＆ペーストして、コード生成を指示します。
2.  **生成されたコードを配置する**: AIが生成したコード（上記の「生成されるNext.jsサーバーコンポーネントのコード例」に類似）を、Next.jsプロジェクト内の適切なパス（例: `app/posts/page.tsx`）に保存します。
3.  **プロジェクトを実行**: 開発サーバーを起動し（`npm run dev` または `yarn dev`）、ブラウザで`/posts`パスにアクセスして、ブログ記事が正しく表示されるか確認します。
4.  **要件に合わせて調整**: データの取得先URL、表示するデータの種類、`revalidate`の時間などを必要に応じて調整してください。

## よくある質問
Q: `fetch` APIの`revalidate`オプションは何ですか？
A: Next.jsの`fetch` API拡張機能で、データのキャッシュをNext.jsのサーバー側でどのように扱うかを定義します。`revalidate: 3600`と設定すると、データは最大で3600秒間（1時間）キャッシュされ、その期間が過ぎると、次回のリクエスト時に自動的に再検証（新しいデータの取得）を試みます。これにより、頻繁に更新されないデータを効率的に扱い、サーバー負荷を軽減できます。

Q: なぜサーバーコンポーネントを使うのですか？
A: サーバーコンポーネントは、サーバー側でデータを取得し、レンダリングを行うため、初期ロードの高速化、JavaScriptバンドルサイズの削減、SEOの向上といったメリットがあります。特に、初期表示に必要なデータを取得・表示する際に強力な選択肢となります。

---
AI Conduit: https://www.youtube.com/@AI.Conduit