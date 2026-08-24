# Claude CodeのNext.js開発で画像最適化が向上しました - 実践テンプレート

## この動画で学んだこと
この動画では、Next.jsアプリケーションにおける画像最適化の重要性と、それを実現するためのNext.jsの`Image`コンポーネントの基本的な使い方を学びました。`Image`コンポーネントを利用することで、自動的に画像を最適化し、Webサイトのパフォーマンスを向上させることができます。

## すぐに使えるテンプレート

Next.jsのプロジェクトで、以下のコードをコピー＆ペーストして画像最適化を体験してください。

// src/app/page.tsx (App Routerの場合) または pages/index.tsx (Pages Routerの場合)

import Image from 'next/image'; // Next.jsのImageコンポーネントをインポート

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Next.js Imageコンポーネントによる画像最適化の例</h1>
      <p>このページでは、Next.jsのImageコンポーネントを使用して画像を効率的に表示する方法を示します。</p>

      {/* 
        従来のimgタグを使用した場合（最適化は手動）
        <img 
          src="/images/sample-legacy.jpg" 
          alt="従来の画像表示" 
          width="500" 
          height="300" 
          style={{ display: 'block', marginBottom: '20px' }}
        />
        上記のようにimgタグを使うと、画像サイズ、フォーマット、遅延ロードなどは開発者が手動で最適化する必要があります。
      */}

      <h2>Next.js Imageコンポーネントの基本</h2>
      <p>
        `Image`コンポーネントは、`src`, `alt`, `width`, `height`プロパティを必須とします。<br />
        `src`には、`public`ディレクトリ内の相対パス、または外部URLを指定します。
      </p>
      <div style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '8px', marginBottom: '20px' }}>
        <Image
          src="/images/nextjs-optimized-image.jpg" // publicディレクトリに配置する画像ファイルのパス
          alt="Next.js Imageコンポーネントで最適化された画像" // 代替テキスト
          width={600} // 画像のオリジナルの幅 (ピクセル単位)。レイアウトシフトを防ぎます。
          height={400} // 画像のオリジナルの高さ (ピクセル単位)。レイアウトシフトを防ぎます。
          priority // この画像がページのLCP (Largest Contentful Paint) 要素である場合に指定し、優先的にロードさせます。
          // sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw" // レスポンシブな画像サイズ指定 (オプション)
          // style={{ objectFit: 'cover' }} // fillプロパティを使用する場合にオブジェクトフィットを指定
          // unoptimized // 最適化を無効にする場合 (開発時や特定の用途向け)
        />
        <p style={{ marginTop: '10px', fontSize: '0.8em', color: '#666' }}>
          `public/images/nextjs-optimized-image.jpg` に画像を配置してください。<br />
          `width`と`height`は、実際の画像のアスペクト比に合わせて設定することが重要です。
        </p>
      </div>

      <h2>Fillプロパティを使用した例 (親要素に合わせて表示)</h2>
      <p>
        `fill`プロパティを使用すると、親要素のサイズに合わせて画像が表示されます。<br />
        この場合、`width`と`height`は不要ですが、親要素に`position: 'relative'`が必要です。
      </p>
      <div style={{ 
          position: 'relative', 
          width: '100%', 
          height: '300px', 
          border: '1px solid #ccc', 
          borderRadius: '8px', 
          overflow: 'hidden' 
      }}>
        <Image
          src="/images/nextjs-background-image.jpg" // publicディレクトリに配置する別の画像ファイル
          alt="親要素に合わせて表示される画像"
          fill // 親要素のサイズに合わせて画像を埋める
          style={{ objectFit: 'cover' }} // 画像の表示方法を指定 (cover, contain, fill, none, scale-down)
          // sizes="(max-width: 768px) 100vw, 50vw" // レスポンシブな画像サイズ指定 (オプション)
        />
        <p style={{ 
            position: 'absolute', 
            bottom: '10px', 
            left: '10px', 
            color: 'white', 
            backgroundColor: 'rgba(0,0,0,0.5)', 
            padding: '5px 10px', 
            borderRadius: '5px',
            fontSize: '0.8em'
        }}>
          `public/images/nextjs-background-image.jpg` に画像を配置してください。<br />
          親要素には `position: 'relative'` とサイズ (width, height) が必要です。
        </p>
      </div>
    </main>
  );
}
## 使い方

1.  **Next.jsプロジェクトの準備:**
    まだNext.jsプロジェクトがない場合は、以下のコマンドで新しいプロジェクトを作成します。
    npx create-next-app@latest my-next-app --typescript --eslint
    # または yarn create next-app my-next-app --typescript --eslint
    cd my-next-app
    2.  **画像ファイルの配置:**
    最適化したい画像ファイル（例: `nextjs-optimized-image.jpg`、`nextjs-background-image.jpg`）を、プロジェクトのルートにある`public`ディレクトリ内の`images`フォルダに配置してください。
    *   例: `my-next-app/public/images/nextjs-optimized-image.jpg`
    *   例: `my-next-app/public/images/nextjs-background-image.jpg`
    (もし`images`フォルダがなければ作成してください。)

3.  **コードのコピー＆ペースト:**
    上記の「すぐに使えるテンプレート」のコードを、以下のいずれかのファイルにコピー＆ペーストして既存の内容を置き換えてください。
    *   **App Routerの場合 (Next.js 13以降推奨):** `src/app/page.tsx`
    *   **Pages Routerの場合:** `pages/index.tsx`

4.  **開発サーバーの起動:**
    プロジェクトのルートディレクトリで以下のコマンドを実行し、開発サーバーを起動します。
    npm run dev
    # または yarn dev
    ブラウザで `http://localhost:3000` にアクセスすると、最適化された画像が表示されることを確認できます。

5.  **外部画像を使用する場合の追加設定:**
    もし外部ドメイン（例: `example.com`）から画像をロードする場合は、`next.config.js`ファイルにそのドメインを追加する必要があります。
    // next.config.js
    /** @type {import('next').NextConfig} */
    const nextConfig = {
      images: {
        // 画像をロードする外部ドメインをここに記述
        // 'your-image-domain.com' は実際のドメインに置き換えてください
        remotePatterns: [
          {
            protocol: 'https',
            hostname: 'assets.example.com', // 例
            port: '',
            pathname: '/my-images/**', // 特定のパスに制限する場合
          },
          // 複数のドメインを追加できます
          {
            protocol: 'https',
            hostname: 'via.placeholder.com', // プレースホルダー画像サイトの例
          },
        ],
      },
    };

    module.exports = nextConfig;
    変更後は、開発サーバーを再起動してください。

## よくある質問

**Q: `Image`コンポーネントで`width`と`height`を指定する必要があるのはなぜですか？**
A: `width`と`height`を指定することで、Next.jsは画像がロードされる前にその領域を確保できます。これにより、画像のロードによってレイアウトがガタつく現象（CLS: Cumulative Layout Shift）を防ぎ、ユーザー体験を向上させます。また、画像の正しいアスペクト比を維持するためにも重要です。

**Q: 外部サイトの画像も最適化できますか？**
A: はい、可能です。ただし、`next.config.js`ファイルに画像のホスト元のドメインを`images.remotePatterns`として追加する必要があります。この設定により、Next.jsは外部の画像もキャッシュし、最適化された形式（WebPなど）で配信できるようになります。

**Q: `Image`コンポーネントを使っているのに、画像が最適化されていないように見えます。**
A: Next.jsの画像最適化は、開発モード（`npm run dev`）では完全には機能しない場合があります。本番ビルド（`npm run build`と`npm run start`）を実行してデプロイすると、WebP変換やサイズ調整などの最適化効果が明確に確認できます。また、ブラウザの開発者ツールでネットワークタブを確認し、画像フォーマットやサイズが変更されているかチェックすることも有効です。

**Q: `layout`プロパティが使えなくなりました。どうすれば良いですか？**
A: Next.js 13以降では、`layout`プロパティは非推奨となり、代わりに`fill`プロパティ、または`width`と`height`の組み合わせでレイアウトを制御することが推奨されています。
*   **固定サイズ:** `width={...} height={...}` を使用。
*   **親要素にフィット:** `fill` プロパティを使用し、親要素に `position: 'relative'` と適切なサイズを指定します。`objectFit` プロパティで画像がどのように親要素にフィットするかを制御できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit