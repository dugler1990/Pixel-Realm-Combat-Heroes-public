from abc import ABC, abstractmethod

class CombatStrategy(ABC):
    @abstractmethod
    def decide_action(self, enemy, player):
        pass
    
    @abstractmethod
    def execute_attack(self, enemy, player):
        pass

    @abstractmethod
    def move(self, enemy, player):
        pass
    
    @abstractmethod
    def parry(self, enemy, player):
        pass
