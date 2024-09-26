import threading

class SpawnerThread(threading.Thread):
    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance

    def run(self):
        while True:
            self.game_instance.layout_manager.spawner.handle_spawn_areas()
