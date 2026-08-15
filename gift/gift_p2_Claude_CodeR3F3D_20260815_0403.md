# Claude CodeのR3Fアニメーションで3Dオブジェクトが簡単に動くようになった - 実践テンプレート

## この動画で学んだこと
この動画では、React Three Fiber (R3F) の`useFrame`フックを活用することで、3Dオブジェクトを簡単にアニメーションさせる方法を学びました。`useRef`でメッシュ要素への参照を取得し、`useFrame`内で`delta`を使って毎フレーム回転させることで、スムーズなアニメーションを実現できます。

## すぐに使えるテンプレート

以下のコードは、シンプルなボックスオブジェクトがY軸とX軸を中心に自動回転するR3Fアプリケーションのテンプレートです。新しいReactプロジェクトを作成し、必要なライブラリをインストールしてからご利用ください。

import React, { useRef } from 'react';
// React Three FiberのCanvasとuseFrameフックをインポート
import { Canvas, useFrame } from '@react-three/fiber';
// @react-three/dreiからカメラコントロールをインポート（オプションだが便利）
import { OrbitControls } from '@react-three/drei';

/**
 * アニメーションする3Dボックスコンポーネント
 * @param {object} props - メッシュに渡すプロパティ (例: position)
 */
function AnimatedBox(props) {
  // 1. アニメーションさせたいメッシュ要素に参照を割り当てます。
  // useRefは、レンダリング間で変更可能な値を保持するために使用されます。
  // ここでは、Three.jsのMeshオブジェクトのインスタンスへの参照を保持します。
  const meshRef = useRef();

  // 2. useFrame内でdeltaを使い毎フレーム要素を回転させます。
  // useFrameは、毎フレーム呼び出されるコールバック関数を登録します。
  // state (Three.jsの状態オブジェクト) と delta (前回のフレームからの経過時間、秒単位) を引数として受け取ります。
  useFrame((state, delta) => {
    // meshRef.currentがnullでないことを確認します（メッシュがマウントされている場合）。
    if (meshRef.current) {
      // 毎フレーム、Y軸にdelta（時間）を加えて回転させます。
      // deltaを使用することで、フレームレートに依存せず、アニメーションが常に同じ速度で実行されます。
      meshRef.current.rotation.y += delta;
      // X軸にも少しゆっくり回転させる例
      meshRef.current.rotation.x += delta * 0.5;
    }
  });

  return (
    // meshRefを<mesh>要素にアタッチし、このメッシュへの参照を取得できるようにします。
    // propsは、親コンポーネントから渡されたpositionなどのプロパティを適用します。
    <mesh {...props} ref={meshRef}>
      {/* サイズ1x1x1のボックスジオメトリ */}
      <boxGeometry args={[1, 1, 1]} />
      {/* 明るいピンクのスタンダードマテリアル */}
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

/**
 * アプリケーションのメインコンポーネント
 */
function App() {
  return (
    // キャンバス全体を覆うようにスタイルを設定
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#282c34' }}>
      {/* Three.jsのシーンを描画するためのCanvasコンポーネント */}
      <Canvas>
        {/* 環境光を追加して、シーン全体のオブジェクトに均一な光を当てます */}
        <ambientLight intensity={0.5} />
        {/* 指向性光を追加して、特定の方向から光を当てます（影の生成など） */}
        <directionalLight position={[10, 10, 5]} intensity={1} />
        
        {/* AnimatedBoxコンポーネントをシーンに追加し、初期位置を設定 */}
        <AnimatedBox position={[0, 0, 0]} />

        {/* OrbitControlsを追加することで、マウスでカメラを操作してオブジェクトを回転・ズームできます */}
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default App;
## 使い方
1.  **新しいReactプロジェクトを作成します。**
    # Viteを使用する場合 (推奨)
    npm create vite@latest my-r3f-app -- --template react
    cd my-r3f-app
    npm install
    
    # Create React Appを使用する場合
    npx create-react-app my-r3f-app
    cd my-r3f-app
    npm install
    2.  **必要なライブラリをインストールします。**
    npm install @react-three/fiber three @react-three/drei
    # または yarn add @react-three/fiber three @react-three/drei
    3.  **`src/App.jsx` (または `src/App.tsx`) の内容を上記のコードに置き換えます。**

4.  **開発サーバーを起動し、ブラウザで確認します。**
    npm run dev # Viteの場合
    npm start   # Create React Appの場合
    ブラウザにアクセスすると、回転するピンクのボックスが表示されるはずです。マウスドラッグでカメラを操作して、様々な角度からオブジェクトを観察できます。

## よくある質問
Q: **なぜ`delta`を使うのですか？**
A: `delta`は前回のフレームからの経過時間（秒）を表します。これを使用することで、アニメーションがユーザーのコンピューターのフレームレートに依存せず、常に同じ速度で実行されるようになります。もし`delta`を使わずに固定値で回転させてしまうと、フレームレートが高い環境では速く、低い環境では遅く見えてしまう可能性があります。

Q: **`useRef`は何のために使うのですか？**
A: `useRef`は、Reactコンポーネントのレンダリングとは独立して値を保持するためのReactフックです。R3Fでは、Three.jsのメッシュやライトなどのオブジェクトインスタンスへの直接的な参照を保持するためによく使われます。これにより、`useFrame`のようなフック内で、レンダリングサイクルとは別にオブジェクトのプロパティ（例: `rotation`、`position`）を直接操作できるようになります。

Q: **アニメーションを一時停止したり、特定の条件で開始/停止したりするにはどうすればいいですか？**
A: `useFrame`フック内のロジックに条件分岐を追加することで実現できます。例えば、`useState`フックを使ってアニメーションの状態を管理し、その状態に基づいて`meshRef.current.rotation`の更新を行うかどうかを決定します。

import React, { useRef, useState } from 'react';
// ...他のインポート

function AnimatedBox(props) {
  const meshRef = useRef();
  const [isAnimating, setIsAnimating] = useState(true); // アニメーションの状態を管理

  useFrame((state, delta) => {
    if (meshRef.current && isAnimating) { // isAnimatingがtrueの場合のみ回転
      meshRef.current.rotation.y += delta;
      meshRef.current.rotation.x += delta * 0.5;
    }
  });

  // クリックでアニメーションをトグルする例
  const handleClick = () => {
    setIsAnimating(!isAnimating);
  };

  return (
    <mesh {...props} ref={meshRef} onClick={handleClick}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={isAnimating ? "hotpink" : "gray"} /> {/* アニメーション状態に応じて色を変える */}
    </mesh>
  );
}
// ...Appコンポーネント
---
AI Conduit: https://www.youtube.com/@AI.Conduit