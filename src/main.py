import asyncio
from telethon import TelegramClient
from src.config import load_config
from src.scheduler_setup import setup_scheduler
from src.message_handler import send_mass_message
from src.data_handler import load_persistent_data, save_persistent_data
from src.logger import setup_logger, get_logger, generate_session_id
from src.cache import Cache
from aiohttp import web
import json

config = load_config()
logger = setup_logger(config)
cache = Cache()

async def setup_client(config):
    logger.info("Setting up Telegram client")
    client = TelegramClient(config['SESSION_FILE'], config['API_ID'], config['API_HASH'])
    await client.start(phone=config['PHONE_NUMBER'])
    logger.info("Telegram client setup complete")
    return client

async def health_check(request):
    return web.Response(text=json.dumps({"status": "healthy"}), content_type='application/json')

async def run_health_check_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("Health check server started on http://localhost:8080/health")

async def run_bot_async():
    session_id = generate_session_id()
    logger.info(f"[{session_id}] Starting bot")
    load_persistent_data()
    
    client = await setup_client(config)
    scheduler = setup_scheduler(client)
    
    await run_health_check_server()
    
    try:
        logger.info(f"[{session_id}] Initiating first mass message send")
        await send_mass_message(client)
        logger.info(f"[{session_id}] Starting scheduler and main loop")
        scheduler.start()
        await keep_bot_running(session_id)
    except Exception as e:
        logger.error(f"[{session_id}] An error occurred: {str(e)}", exc_info=True)
    finally:
        await cleanup(client, scheduler, session_id)

async def keep_bot_running(session_id):
    logger.info(f"[{session_id}] Bot is now running")
    try:
        while True:
            await asyncio.sleep(60)  # Reduced frequency of this log
            logger.debug(f"[{session_id}] Bot still running")
    except asyncio.CancelledError:
        logger.info(f"[{session_id}] Bot execution cancelled")

async def cleanup(client, scheduler, session_id):
    logger.info(f"[{session_id}] Cleaning up...")
    if scheduler.running:
        scheduler.shutdown()
    await client.disconnect()
    save_persistent_data()
    logger.info(f"[{session_id}] Cleanup complete.")

def run_bot():
    logger.info("Initializing bot")
    try:
        asyncio.run(run_bot_async())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    run_bot()
