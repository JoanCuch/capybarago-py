from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
import copy

@dataclass
class Log:
    
    class Action(Enum) :
        ROUND_COMPLETED = "round_completed"
        META_STAT_LEVEL_UP = "meta_stat_level_up"
        DAY_COMPLETED = "day_completed"
        CHAPTER_VICTORY = "chapter_victory"
        CHAPTER_DEFEAT = "chapter_defeat"
        PLAYER_ATTACK = "player_attack"
        ENEMY_ATTACK = "enemy_attack"
        BATTLE_VICTORY = "battle_victory"
        BATTLE_DEFEAT = "battle_defeat"
        PLAYER_NEW_SESSION = "player_new_session"
        PLAYER_NEW_DAY = "player_new_day"


    _logs: list

    @staticmethod
    def initialize():
        _logs = []
        return Log(_logs=_logs)

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
    def log_round_completed(self, time_log: Dict[str, Any],chapter_level: int, victory: bool, rounds_done: int):
        log_entry = {
                "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
                "action": self.Action.ROUND_COMPLETED.value,
                "message": f"Round {rounds_done} completed: Chapter {chapter_level} ended in {'Victory' if victory else 'Defeat'}",
                "rounds_done": rounds_done,
                "chapter_level": chapter_level,
                "victory": victory,
            }
        self._logs.append(log_entry)


    def log_stat_level_up(self,time_log: Dict[str, Any], stat_name: str, new_level: int):
        log_entry = {
            "day": time_log.get("day", 999),
            "day_session": time_log.get("day_session", 999),
            "session_time": time_log.get("session_time", 999),
            "action": self.Action.META_STAT_LEVEL_UP.value,
            "message": f"Stat {stat_name} leveled up to {new_level}",
            "stat_name": stat_name,
            "new_level": new_level
        }
        self._logs.append(log_entry)


    def log_day_completed(self,time_log: Dict[str, Any], day_num: int, chapter_num: int, event_type, event_param):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.DAY_COMPLETED.value,
            "message": f"Day {day_num} completed for Chapter {chapter_num} with event {event_type}",
            "day_num": day_num,
            "chapter_num": chapter_num,
            "event_type": event_type,
            "event_param": event_param
        }
        self._logs.append(log_entry)

    def log_chapter_victory(self, time_log: Dict[str, Any], chapter_num: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.CHAPTER_VICTORY.value,
            "message": f"Chapter {chapter_num} completed with victory",
            "chapter_num": chapter_num
        }
        self._logs.append(log_entry)

    def log_chapter_defeat(self,time_log: Dict[str, Any], chapter_num: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.CHAPTER_DEFEAT.value,
            "message": f"Chapter {chapter_num} completed with defeat",
            "chapter_num": chapter_num
        }
        self._logs.append(log_entry)

    def log_player_attack(self, time_log: Dict[str, Any],damage: int, enemy_type: str, enemy_hp: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.PLAYER_ATTACK.value,
            "message": f"Player attacked {enemy_type} for {damage} damage",
            "damage": damage,
            "enemy_type": enemy_type,
            "enemy_hp": enemy_hp
        }
        self._logs.append(log_entry)

    def log_enemy_attack(self,time_log: Dict[str, Any], damage: int, enemy_type: str, player_hp: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.ENEMY_ATTACK.value,
            "message": f"{enemy_type} attacked player for {damage} damage",
            "damage": damage,
            "player_hp": player_hp,
            "enemy_type": enemy_type
        }
        self._logs.append(log_entry)

    def log_battle_victory(self, time_log: Dict[str, Any],enemy_type: str, player_hp: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.BATTLE_VICTORY.value,
            "message": f"Battle won against {enemy_type}",
            "enemy_type": enemy_type,
            "player_hp": player_hp
        }
        self._logs.append(log_entry)

    def log_battle_defeat(self, time_log: Dict[str, Any],enemy_type: str, enemy_hp: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.BATTLE_DEFEAT.value,
            "message": f"Battle lost against {enemy_type}",
            "enemy_type": enemy_type,
            "enemy_hp": enemy_hp
        }
        self._logs.append(log_entry)

    def log_player_new_session(self, time_log: Dict[str, Any],session_num: int, day_num: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.PLAYER_NEW_SESSION.value,
            "message": f"Player started new session {session_num} on day {day_num}",
            "session_num": session_num,
            "day_num": day_num
        }
        self._logs.append(log_entry)

    def log_player_new_day(self, time_log: Dict[str, Any],day_num: int):
        log_entry = {
            "day": time_log.get("day", 999),
                "day_session": time_log.get("day_session", 999),
                "session_time": time_log.get("session_time", 999),
            "action": self.Action.PLAYER_NEW_DAY.value,
            "message": f"Player started new day {day_num}",
            "day_num": day_num
        }
        self._logs.append(log_entry)