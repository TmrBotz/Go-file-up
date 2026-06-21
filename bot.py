import os
import asyncio
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import Message
from gofile import upload_to_gofile
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
GOFILE_TOKEN = os.environ["GOFILE_TOKEN"]
PORT = int(os.environ.get("PORT", 8080))

# Dummy HTTP server for Render port binding
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http():
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

app = Client("gofile_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & (
    filters.document | filters.video | filters.photo | filters.audio
))
async def handle_file(client: Client, message: Message):
    msg = await message.reply("⬇️ Downloading...")

    try:
        file_path = await message.download(in_memory=True)
        file_bytes = bytes(file_path.getbuffer())

        if message.document:
            filename = message.document.file_name or "file"
        elif message.video:
            filename = message.video.file_name or "video.mp4"
        elif message.photo:
            filename = "photo.jpg"
        elif message.audio:
            filename = message.audio.file_name or "audio.mp3"
        else:
            filename = "file"

        await msg.edit("⬆️ Uploading to GoFile...")

        result = await upload_to_gofile(file_bytes, filename, GOFILE_TOKEN)

        await msg.edit(
            f"✅ **Uploaded Successfully!**\n\n"
            f"📄 **File:** `{result['filename']}`\n\n"
            f"🔗 **Link:** {result['link']}"
        )

    except Exception as e:
        await msg.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply(
        "👋 **GoFile Upload Bot**\n\n"
        "Koi bhi file bhejo — PDF, Video, Photo, Audio\n"
        "Main GoFile pe upload karke link de dunga! 🚀"
    )

if __name__ == "__main__":
    Thread(target=run_http, daemon=True).start()
    print(f"HTTP server running on port {PORT}")
    print("Bot started...")
    app.run()
