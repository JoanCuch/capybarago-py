from dataclasses import dataclass, field
from typing import List, Dict, Any
import pandas as pd
import random
import streamlit as st
import config_import as config_import
from config_import import ConfigKeys



@dataclass
class Meta_stat:
    name: str = ""
    initial_value: int = 0
    meta_bonus_base: int = 0
    meta_bonus_exp: int = 0
    meta_cost_base: int = 0
    meta_cost_exp: int = 0
    level: int = 0

    def get_bonus(self) -> int:
        return self.meta_bonus_base + self.meta_bonus_exp * self.level
    
    def get_cost(self) -> int:
        return self.meta_cost_base + self.meta_cost_exp * self.level
    
    def level_up(self):
        self.level += 1

@dataclass
class Player_meta_progress:
    stat_atk: Meta_stat
    stat_def: Meta_stat
    stat_max_hp: Meta_stat
    
    gold: int = 0
    chapter: int = 0

    @staticmethod
    def initialize_from_config(config_df) -> 'Player_meta_progress':
        stat_atk = Meta_stat(
            name= config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_NAME.value].iloc[0],
            initial_value= config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_INITIAL_VALUE.value].iloc[0],
            meta_bonus_base=config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_META_BONUS_BASE.value].iloc[0],
            meta_bonus_exp=config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_META_BONUS_EXP.value].iloc[0],
            meta_cost_base=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_META_COST_BASE.value].iloc[0]),
            meta_cost_exp=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_ATK.value, ConfigKeys.STAT_META_COST_EXP.value].iloc[0]),
            level=0
        )
        stat_def = Meta_stat(
            name= config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_NAME.value].iloc[0],
            initial_value= config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_INITIAL_VALUE.value].iloc[0],
            meta_bonus_base=config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_META_BONUS_BASE.value].iloc[0],
            meta_bonus_exp=config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_META_BONUS_EXP.value].iloc[0],
            meta_cost_base=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_META_COST_BASE.value].iloc[0]),
            meta_cost_exp=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_DEF.value, ConfigKeys.STAT_META_COST_EXP.value].iloc[0]),
            level=0
        )
        stat_max_hp = Meta_stat(
            name="max_hp",
            initial_value=config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_MAX_HP.value, ConfigKeys.STAT_INITIAL_VALUE.value].iloc[0],
            meta_bonus_base=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_MAX_HP.value, ConfigKeys.STAT_META_BONUS_BASE.value].iloc[0]),
            meta_bonus_exp=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_MAX_HP.value, ConfigKeys.STAT_META_BONUS_EXP.value].iloc[0]),
            meta_cost_base=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_MAX_HP.value, ConfigKeys.STAT_META_COST_BASE.value].iloc[0]),
            meta_cost_exp=int(config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == ConfigKeys.STAT_MAX_HP.value, ConfigKeys.STAT_META_COST_EXP.value].iloc[0]),
            level=0
        )       
        gold = 0
        chapter = 0

        return Player_meta_progress(
            stat_atk=stat_atk,
            stat_def=stat_def,
            stat_max_hp=stat_max_hp,
            gold=gold,
            chapter=chapter
        )

@dataclass
class PlayerCharacter:
    stat_atk: int
    stat_def: int
    stat_hp: int
    stat_max_hp: int

    def modify_atk(self, value: int):
        self.stat_atk += value

    def modify_def(self, value: int):
        self.stat_def += value

    def modify_hp(self, value: int):
        self.stat_hp = min(self.stat_hp + value, self.stat_max_hp)

    def is_dead(self) -> bool:
        return self.stat_hp <= 0
    
    


@dataclass
class EnemyCharacter:
    type: str
    stat_atk: int
    stat_def: int
    stat_max_hp: int
    stat_hp: int

    def modify_atk(self, value: int):
        self.stat_atk += value

    def modify_def(self, value: int):
        self.stat_def += value

    def modify_hp(self, value: int):
        self.stat_hp = min(self.stat_hp + value, self.stat_max_hp)

    def is_dead(self) -> bool:
        return self.stat_hp <= 0


@dataclass
class Simulation_Log:
    chapters_log : List[Dict['str','Chapter_Log']] = field(default_factory=list)
    #TODO

@dataclass
class Chapter_Log:
    status: str  # 'win' | 'lose' | 'ongoing'
    daily_log: List[Dict[str, Any]] = field(default_factory=list)

    def add_day(self, day: int, event_name: str, player: PlayerCharacter):
        self.daily_log.append({
            "day": day,
            "event_name": event_name,
            "player_atk": player.stat_atk,
            "player_def": player.stat_def,
            "player_hp": player.stat_hp,
            "player_maxhp": player.stat_max_hp,
            "player_delta_atk": self.daily_log[-1]["player_atk"]-player.stat_atk if self.daily_log else 0,
            "player_delta_def": self.daily_log[-1]["player_def"]-player.stat_def if self.daily_log else 0,
            "player_delta_hp": self.daily_log[-1]["player_hp"]-player.stat_hp if self.daily_log else 0,
            "player_delta_maxhp": self.daily_log[-1]["player_maxhp"]-player.stat_max_hp if self.daily_log else 0
        })

def get_config_value(config_df, row_key: ConfigKeys, column_key: ConfigKeys) -> int:
    return config_df.loc[config_df[ConfigKeys.STAT_NAME.value] == row_key.value, column_key.value].iloc[0]
   
def simulate_battle(player: PlayerCharacter, enemy: EnemyCharacter) ->  List[str]:
    
    battle_log = []

    while not player.is_dead() and not enemy.is_dead():
        # Player attacks enemy
        damage_to_enemy = max(0, player.stat_atk - enemy.stat_def)
        enemy.modify_hp(-damage_to_enemy)
        battle_log.append(f"Player attacks {enemy.type} for {damage_to_enemy} damage. Enemy HP: {enemy.stat_hp}/{enemy.stat_max_hp}")

        if enemy.is_dead():
            battle_log.append(f"{enemy.type} defeated!")
            break

        # Enemy attacks player
        damage_to_player = max(0, enemy.stat_atk - player.stat_def)
        player.modify_hp(-damage_to_player)
        battle_log.append(f"{enemy.type} attacks player for {damage_to_player} damage. Player HP: {player.stat_hp}/{player.stat_max_hp}")

        if player.is_dead():
            battle_log.append("Battle ended: Player defeated!")
            break

    st.dataframe(battle_log)
    battle_log.append("Battle ended")
    return battle_log

def simulate_chapter(player: PlayerCharacter, events: List[Dict]) -> Chapter_Log:

    chapter_log = Chapter_Log(status="ongoing")
    day = 0

    chapter_log.add_day(day, "start", player)

    for event in events:
        day += 1

        if event["type"] == "battle":
            simulate_battle(player, event["apply"])
            chapter_log.add_day(day, event["type"], player)
            st.write(f"Day {day}: Battle with {event['apply'].type} completed, player stats: atk={player.stat_atk}, def={player.stat_def}, hp={player.stat_hp}/{player.stat_max_hp}")
        else:
            event["apply"](player)
            chapter_log.add_day(day, event["type"], player)
            st.write(f"Day {day}: {event['type']} applied, player stats: atk={player.stat_atk}, def={player.stat_def}, hp={player.stat_hp}/{player.stat_max_hp}")   

        if player.is_dead():
            chapter_log.status = "lose"
            return chapter_log

    chapter_log.status = "win"
    return chapter_log

def initialize_chapter_config(daily_event_df, enemies_df) -> List[Dict]:

    events = []

    for _, row in daily_event_df.iterrows():
        daily_event = row.iloc[0]
        daily_event_param = row.iloc[1]

        if daily_event == "atk":
            events.append({"type": "atk", "apply": lambda player, n=daily_event_param: player.modify_atk(n)})
        elif daily_event == "def":
            events.append({"type": "def", "apply": lambda player, n=daily_event_param: player.modify_def(n)})
        elif daily_event == "hp":
            events.append({"type": "hp", "apply": lambda player, n=daily_event_param: player.modify_hp(n)})
        elif daily_event == "battle":
            enemy_row = enemies_df[enemies_df["enemy_type"] == daily_event_param].iloc[0]
            events.append({
                "type": "battle",
                "apply": EnemyCharacter(
                    type=enemy_row["enemy_type"],
                    stat_atk=int(enemy_row["enemy_atk"]),
                    stat_def=int(enemy_row["enemy_def"]),
                    stat_max_hp=int(enemy_row["enemy_max_hp"]),
                    stat_hp=int(enemy_row["enemy_max_hp"])
                )
            })

    return events

def initialize_player_character(config_df) -> PlayerCharacter:
    stat_atk = get_config_value(config_df, ConfigKeys.STAT_ATK, ConfigKeys.STAT_INITIAL_VALUE)
    stat_def = get_config_value(config_df, ConfigKeys.STAT_DEF, ConfigKeys.STAT_INITIAL_VALUE)
    stat_max_hp = get_config_value(config_df, ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_INITIAL_VALUE)
    stat_hp = stat_max_hp

    player = PlayerCharacter(stat_atk=stat_atk, stat_def=stat_def, stat_hp=stat_hp, stat_max_hp=stat_max_hp)
    return player

def simulate_meta_progression(meta_progress: Player_meta_progress) -> Player_meta_progress:
    # Simulate the meta progression for the player
    # This is a placeholder for the actual progression logic
    meta_progress.gold += 10
    return meta_progress

def model(config_df) -> List[Chapter_Log]:
    chapter_logs = []

    player_config = config_import.get_player_config()
    meta_progress = Player_meta_progress.initialize_from_config(player_config)

    # Chapters Sequence Loop
    for chapter_number in range(1, 4):  # Capítols 1, 2 i 3
        st.write(f"Simulating Chapter {chapter_number}")

        chapter_df = config_import.get_chapter_config(chapter_number)
        enemies_df = config_import.get_enemy_config()
        player_df = config_import.get_player_config()
        player = initialize_player_character(player_df)

        # Llegeix la configuració d'events i enemics
        chapter_config = initialize_chapter_config(chapter_df, enemies_df)

        # Simula el capítol
        chapter_log = simulate_chapter(player, chapter_config)
        chapter_logs.append(chapter_log)

        # Si el jugador mor, finalitza la run
        if chapter_log.status == "lose":
            break

    return chapter_logs
