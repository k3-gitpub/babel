import asyncio
from scene_test_sandbox import TestSandboxScene

# このファイルが実行されていることを確認するためのプリント文です。
print("--- EXECUTING run_sandbox.py ---")

async def main():
    """
    TestSandboxSceneを直接起動するための非同期メイン関数。
    Webビルド時にアセットを登録する処理もここで行う。
    """
    # --- Webビルド(pygbag)のためのアセット登録と初期化 ---
    try:
        from pygbag import preloader
        await preloader.run(log_missing=True)
    except ImportError:
        # pygbagがインストールされていないローカル実行環境では何もしない
        pass

    print("Starting Test Sandbox Scene...")
    sandbox_scene = TestSandboxScene()
    await sandbox_scene.run()

if __name__ == '__main__':
    asyncio.run(main())