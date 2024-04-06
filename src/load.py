import asyncio
import json
import aiohttp

from telethon import TelegramClient, events, sync
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import UserFull

api_id = 29549090
api_hash = "baf8e0f7276ce0841af46f92f305c0ff"

client = TelegramClient("testing", api_id, api_hash)
client.start()


async def start():
    sheetId = "1Edy0_vI_vObETD96SI-FnRJqtNuPy0dVu64kl-_CsE0"
    sheetGid = "1816724719"
    url = f"https://docs.google.com/spreadsheets/d/{sheetId}/gviz/tq?tqx=out:json&tq&gid={sheetGid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

            data = json.loads(text[47 : len(text) - 2])

            rows = data["table"]["rows"]

            users = dict()

            for index, row in enumerate(rows):
                if index > 1 and row["c"][0] != None:
                    latitude = row["c"][0]["v"]
                    longitude = row["c"][1]["v"]
                    username = row["c"][3]["v"]
                    name = row["c"][4]["v"]

                    try:
                        full = await client(GetFullUserRequest(username))
                    except Exception as e:
                        print(e)

                    if full and full.full_user:
                        info: UserFull = full.full_user

                        if info.id in users:
                            users[info.id]["location"].append(
                                {
                                    "name": name,
                                    "latitude": latitude,
                                    "longitude": longitude,
                                }
                            )
                        else:
                            users[info.id] = {
                                "location": [
                                    {
                                        "latitude": latitude,
                                        "longitude": longitude,
                                    }
                                ],
                                "name": name,
                                "username": username,
                                "id": info.id,
                            }

            with open("users.json", "w") as outfile:
                outfile.write(json.dumps(users))


# No user has "justbackoff" as username
# No user has "saturday_hope" as username
# No user has "iurii_avakian" as username
# No user has "ilyaaa_u" as username

with client:
    client.loop.run_until_complete(start())
