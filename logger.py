from enum import Enum
from dataclasses import dataclass
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
    ROUND_COMPLETED = "round_completed"

@dataclass
class Log:
    _logs: list

    @staticmethod
    def initialize():
        _logs = []
        return Log(_logs=_logs)

    def add_log(self, actor: Log_Actor, granularity: Log_Granularity, action: Log_Action, message: str, payload: dict):
        log_entry = {
            "actor": actor.value,
            "granularity": granularity.value,
            "action": action.value,
            "message": message,
            "payload": copy.deepcopy(payload) if payload else {},
        }
        self._logs.append(log_entry)

    def get_logs(self):
        return self._logs

    def clear_logs(self):
        self._logs = []

    def get_logs_as_dataframe(self):
        import pandas as pd
        return pd.DataFrame(self._logs)

    def has_logs(self):
        return len(self._logs) > 0
    
    def get_flattened_logs_df(self):
        import pandas as pd
        raw_logs = self.get_logs_as_dataframe().to_dict(orient="records")

        flattened_df = pd.json_normalize(
            raw_logs,
            sep="."  # aplanar tots els nivells amb noms com 'payload.player_character.hp'
        )

        if "payload" in flattened_df.columns:
            flattened_df = flattened_df.drop(columns=["payload"])

        return flattened_df
    
    ## ------ Action Logs ------
    def log_round_completed(self, chapter_level: int, victory: bool, rounds_done: int):
        log_entry = {
                "actor": Log_Actor.SIMULATION.value,
                "granularity": Log_Granularity.CHAPTER.value,
                "action": Log_Action.ROUND_COMPLETED.value,
                "message": f"Round {rounds_done} completed: Chapter {chapter_level} ended in {'Victory' if victory else 'Defeat'}",
                "rounds_done": rounds_done,
                "chapter_level": chapter_level,
                "victory": victory,
            }
        self._logs.append(log_entry)

        #  self.add_log(
        #     Log_Actor.SIMULATION,
        #     Log_Granularity.CHAPTER,
        #     Log_Action.ROUND_COMPLETED,
        #     f"Round {rounds_done} completed: Chapter {chapter_level} ended in {'Victory' if victory else 'Defeat'}",
        #     {
        #         "round": rounds_done,
        #         "chapter": chapter_level,
        #         "victory": victory
        #     } 
        # )