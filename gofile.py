import aiohttp

GOFILE_API = "https://api.gofile.io"

async def get_best_server() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GOFILE_API}/servers") as resp:
            data = await resp.json()
            return data["data"]["servers"][0]["name"]

async def upload_to_gofile(file_bytes: bytes, filename: str, token: str) -> dict:
    server = await get_best_server()
    url = f"https://{server}.gofile.io/contents/uploadfile"

    form = aiohttp.FormData()
    form.add_field("file", file_bytes, filename=filename)
    form.add_field("token", token)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form) as resp:
            data = await resp.json()
            if data["status"] == "ok":
                return {
                    "link": data["data"]["downloadPage"],
                    "file_id": data["data"]["id"],
                    "filename": filename
                }
            else:
                raise Exception(f"GoFile upload failed: {data}")
