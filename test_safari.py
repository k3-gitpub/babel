import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
    """
    Playwrightを起動し、iPhone Safariの挙動をエミュレートします。
    """
    # 1. WebKitブラウザをヘッドフルモードで起動します。
    #    headless=False にすることで、ブラウザのウィンドウが表示され、
    #    操作を目で確認できます。
    browser = await playwright.webkit.launch(headless=False)

    # 2. iPhone 13 Proのデバイス情報を取得します。
    #    'iPhone 11', 'iPhone 12' など他の機種も選択可能です。
    #    https://playwright.dev/python/docs/emulation#devices
    iphone_13_pro = playwright.devices['iPhone 13 Pro']

    # 3. ランドスケープ（横向き）モードにするためにviewportの幅と高さを入れ替えます。
    #    元の辞書を直接変更しないようにコピーを作成するのが安全です。
    landscape_iphone_info = iphone_13_pro.copy()
    original_viewport = landscape_iphone_info['viewport']
    landscape_iphone_info['viewport'] = {
        'width': original_viewport['height'],
        'height': original_viewport['width']
    }

    # 4. iPhone 13 Pro（ランドスケープモード）をエミュレートするコンテキストを作成します。
    context = await browser.new_context(**landscape_iphone_info)

    # 5. 新しいページを開きます。
    page = await context.new_page()

    # 6. ローカルサーバーで実行中のアプリにアクセスします。
    try:
        print("Accessing http://localhost:8000 ...")
        await page.goto("http://localhost:8000")
        print("Successfully accessed the page.")
        print("\n--- 確認してください ---")
        print("表示されたウィンドウで、iPhone実機と同じように 'Click to Start' 画面から進まない問題が再現されるか確認してください。")
        print("ウィンドウ上でクリック操作などを試すことができます。")

        # 7. Playwright Inspectorを起動してデバッグを容易にします。
        #    ここでスクリプトの実行が一時停止し、操作用のGUIが表示されます。
        #    - "Resume"ボタン(▷)を押すか、ウィンドウを閉じるとスクリプトが終了します。
        #    - "Record"機能で操作を記録し、コードを生成することもできます。
        print("\nPlaywright Inspectorを起動します。操作を試した後、ウィンドウを閉じてください。")
        await page.pause()

    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"ページへのアクセスに失敗しました: {e}")
        print("ステップ1で起動したローカルWebサーバーが、別のターミナルで正しく実行されているか確認してください。")

    finally:
        # 8. ブラウザを閉じます。
        print("Closing browser...")
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    print("--- Playwright iPhone Safari Emulation ---")
    asyncio.run(main())
    print("Test finished.")