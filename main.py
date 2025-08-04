import asyncio

print("--- EXECUTING test_pygbag.py ---")
print("If you can see this message, pygbag's basic functions are working!")

async def main():
    print("Async main function has started.")
    counter = 0
    while counter < 10:
        print(f"Loop count: {counter}")
        await asyncio.sleep(1)
        counter += 1
    print("Test finished.")

if __name__ == "__main__":
    print("Starting asyncio event loop.")
    asyncio.run(main())