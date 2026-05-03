import asyncio
import logging
from config import SOURCE_CHANNELS, TARGET_CHANNEL, CUSTOM_MAPPING

logger = logging.getLogger(__name__)

class Dumper:
    def __init__(self, client_manager, db):
        self.client = client_manager
        self.db = db
        self.is_running = False
        self.tasks = []
    
    async def dump_loop(self, source_id):
        target_id = CUSTOM_MAPPING.get(source_id, TARGET_CHANNEL)
        
        while self.is_running:
            try:
                active, last_id = self.db.get_dumping_status(source_id)
                if not active:
                    await asyncio.sleep(5)
                    continue
                
                messages = await self.client.get_messages(source_id, limit=50, offset_id=last_id)
                
                dumped_count = 0
                for msg in messages:
                    if msg.id <= last_id:
                        continue
                    if not self.db.is_already_dumped(source_id, msg.id):
                        if await self.client.forward_message(target_id, msg):
                            self.db.add_dumped_message(source_id, msg.id, target_id)
                            self.db.increment_stat(source_id)
                            dumped_count += 1
                            self.db.update_last_message_id(source_id, msg.id)
                    
                    if msg.id > last_id:
                        self.db.update_last_message_id(source_id, msg.id)
                
                if dumped_count > 0:
                    logger.info(f"Dumped {dumped_count} from {source_id} to {target_id}")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error dumping from {source_id}: {e}")
                await asyncio.sleep(10)
    
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        for src in SOURCE_CHANNELS:
            task = asyncio.create_task(self.dump_loop(src))
            self.tasks.append(task)
        logger.info(f"Dumper started for {len(SOURCE_CHANNELS)} sources")
    
    async def stop(self):
        self.is_running = False
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        logger.info("Dumper stopped")
