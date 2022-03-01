# This example requires an api key (obviously)

import hypixel
import asyncio

description = """A simple example that shows how to get a key's queries."""

async def main():
    client = hypixel.Client()
    async with client:
        try:
            key = await client.key('api-key')
            print(key.queries)
        except HypixelException as error:
            print(error.text)

if __name__ == '__main__':
    asyncio.run(main())
