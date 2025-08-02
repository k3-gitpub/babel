import asyncio
import sys

# このプログラムはPygameを一切使用しません。
# Pythonのコードがブラウザ上で実行され、コンソールに文字を出力できるか、という
# 最も基本的な機能のみをテストします。

async def main():
    print("--- Hello World Test Program ---")
    print("This test does not use Pygame.")
    print("If you see this message in the developer console, the basic Python runtime is working.")

    running = True
    count = 0
    while running:
        count += 1
        print(f"Program is running... count: {count}")
        # ブラウザがプログラムを終了しないように、ループを維持します。
        await asyncio.sleep(1)

    print("Program finished.")

if __name__ == "__main__":
    asyncio.run(main())