# Claude CodeのuseFrameで3Dアニメーション - 実践テンプレート

## この動画で学んだこと
React Three Fiberの`useFrame`と`ref`を組み合わせることで、3Dオブジェクトの描画を毎フレーム自動で更新し、簡単にアニメーションを作成できることを学びました。これにより、複雑なレンダリングループの管理から解放され、宣言的に3Dアニメーションを実装できます。

## すぐに使えるテンプレート

まずは、新しいReactプロジェクトを作成し、必要なライブラリをインストールしましょう。

# 1. 新しいReactプロジェクトを作成 (Viteを使用するのがおすすめです)
npm create vite@latest my-r3f-animation -- --template react

# 2. プロジェクトディレクトリに移動
cd my-r3f-animation

# 3. React Three Fiber (R3F) と Three.js をインストール
# @react-three/drei は、R3Fを便利にするユーティリティ集です (OrbitControlsなど)
npm install @react-three/fiber three @react-three/drei

# 4. 開発サーバーを起動して確認
npm run dev
次に、`src/App.jsx` ファイルを以下の内容で上書きしてください。

// src/App.jsx

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei'; // カメラコントロールのためのユーティリティ

// アニメーションするボックスコンポーネント
function AnimatedBox() {
  // ① useRefを使って、3Dオブジェクトのインスタンスを参照
  // meshRef.current には、このmesh要素がレンダリングするThree.jsのMeshオブジェクトが格納されます
  const meshRef = useRef();

  // ② useFrameフックは、毎フレーム自動で呼び出されます
  // state: WebGLRenderer, camera, sceneなどの現在の描画状態
  // delta: 最後のフレームからの経過時間（秒）。アニメーションをフレームレートに依存させないために非常に重要です
  useFrame((state, delta) => {
    // meshRef.current が存在することを確認
    if (meshRef.current) {
      // X軸を中心に回転を更新
      // deltaを乗算することで、どのフレームレートでも同じ速度で回転します
      meshRef.current.rotation.x += delta;
      // Y軸を中心に回転を更新 (X軸とは少し異なる速度で)
      meshRef.current.rotation.y += delta * 0.5;
    }
  });

  return (
    // meshコンポーネントはThree.jsのMeshオブジェクトを作成します
    // refを渡すことで、useFrame内でこのオブジェクトにアクセスできるようになります
    <mesh ref={meshRef}>
      {/* boxGeometryは1x1x1の立方体ジオメトリを作成します */}
      <boxGeometry args={[1, 1, 1]} />
      {/* meshStandardMaterialは物理ベースレンダリングのマテリアルで、光沢や影を表現できます */}
      <meshStandardMaterial color="hotpink" /> {/* オブジェクトの色をホットピンクに設定 */}
    </mesh>
  );
}

// メインのAppコンポーネント
function App() {
  return (
    // キャンバス全体を覆うようにスタイルを設定
    <div style={{ width: '100vw', height: '100vh', background: '#282c34' }}>
      {/* Canvasコンポーネントは、React Three Fiberのレンダリングコンテキストを提供します */}
      {/* cameraプロパティで初期カメラ位置と視野角を設定 */}
      <Canvas camera={{ position: [0, 0, 3], fov: 75 }}>
        {/* 環境光を追加: シーン全体を均一に照らす */}
        <ambientLight intensity={0.5} />
        {/* 点光源を追加: 特定の位置から光を放つ (影やハイライトに影響) */}
        <pointLight position={[10, 10, 10]} intensity={1} />

        {/* アニメーションするボックスコンポーネントをキャンバス内に配置 */}
        <AnimatedBox />

        {/* OrbitControlsを追加: マウス操作でカメラを動かせるようになります */}
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default App;
## 使い方
1.  **新しいReactプロジェクトの作成**: 上記の`npm create vite@latest ...` コマンドを実行し、Reactプロジェクトを作成します。
2.  **必要なライブラリのインストール**: プロジェクトディレクトリに移動後、`npm install @react-three/fiber three @react-three/drei` コマンドでライブラリをインストールします。
3.  **コードのコピー&ペースト**: `src/App.jsx` ファイルの内容を、上記テンプレートのコードで上書きします。
4.  **開発サーバーの起動**: `npm run dev` コマンドを実行し、ブラウザで `http://localhost:5173` (または表示されるURL) にアクセスします。
5.  **結果の確認**: ホットピンクの立方体が、X軸とY軸を中心に自動で回転しているのが確認できます。マウスでドラッグすると、視点を変更できます。

## よくある質問
Q: `delta`って具体的に何ですか？
A: `delta`は、前回のフレームがレンダリングされてから今回のフレームがレンダリングされるまでの経過時間（秒単位）です。これをアニメーション速度に乗算することで、ユーザーのPCの性能やディスプレイのフレームレートに関わらず、アニメーションが常に同じ速度に見えるようになります。もし`delta`を使わない場合、フレームレートが高い環境ではアニメーションが速く、低い環境では遅く見えてしまいます。

Q: `useFrame`で回転以外のこともアニメーションできますか？
A: はい、もちろんです！`meshRef.current`を通じてアクセスできるThree.jsオブジェクトのあらゆるプロパティをアニメーションできます。例えば、`position`（位置）、`scale`（スケール）、`material.color`（マテリアルの色）、`geometry.vertices`（ジオメトリの頂点）なども`useFrame`内で更新することで、様々な動的な表現が可能です。

Q: このコードを実行するには他に何が必要ですか？
A: Node.jsとnpm (またはYarn) がインストールされている必要があります。これらはJavaScriptのランタイム環境とパッケージマネージャーであり、ReactやReact Three Fiberなどのプロジェクトを開発・実行するために不可欠です。

---
AI Conduit: https://www.youtube.com/@AI.Conduit