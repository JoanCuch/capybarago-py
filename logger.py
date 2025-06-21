from enum import Enum
import copy

class Log_Actor (Enum):
    PLAYER=  "player"
    GAME= "game"
    SIMULATION= "simulation"

class Log_Granularity (Enum):
    SIMULATION = "simulation"
    META= "meta"
    CHAPTER = "chapter"
    DAY = "day"
    BATTLE = "battle"
    TURN = "turn"

class Log_Action(Enum) :
    INITIALIZE = "initialize"
    SIMULATE = "simulate"
    END = "end"
    PLAYER_ATTACK = "player_attack"
    ENEMY_ATTACK = "enemy_attack"
    PLAYER_DEFEATED = "player_defeated"
    ENEMY_DEFEATED = "enemy_defeated"

class Logger:
    _logs = []

    @classmethod
    def add_log(cls, actor: Log_Actor, granularity: Log_Granularity, action: Log_Action, message: str, payload: dict):
        log_entry = {
            "actor": actor.value,
            "granularity": granularity.value,
            "action": action.value,
            "message": message,
            "payload": copy.deepcopy(payload) if payload else {},
        }
        cls._logs.append(log_entry)

    @classmethod
    def get_logs(cls):
        return cls._logs

    @classmethod
    def clear_logs(cls):
        cls._logs = []