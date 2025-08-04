from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import pandas as pd
import config_import as config_import
from config_import import ConfigKeys, Config
from enum import Enum
from logger import Log, Log_Actor, Log_Granularity,Log_Action

@dataclass
class Meta_stat:
    name: str = ""
    initial_value: int = 0
    meta_bonus_base: int = 0
    meta_bonus_exp: int = 0
    meta_cost_base: int = 0
    meta_cost_exp: int = 0
    level: int = 0

    def get_value(self) -> int:
        return self.initial_value + self.meta_bonus_exp * self.level
    
    def get_bonus_increment(self) -> int:
        return self.initial_value + self.meta_bonus_exp * (self.level + 1) - (self.initial_value + self.meta_bonus_exp * self.level)

    def get_cost(self) -> int:
        return self.meta_cost_base + self.meta_cost_exp * self.level

    def level_up(self):
        self.level += 1

    def get_level(self) -> int:
        return self.level

@dataclass
class Player_meta_progression:

    log: Log

    stat_atk: Meta_stat
    stat_def: Meta_stat
    stat_max_hp: Meta_stat
    
    gold: int = 0
    chapter_level: int = 0


    @staticmethod
    def initialize(player_config_df, log: Log) -> 'Player_meta_progression':
        stat_atk = Meta_stat(
            name=get_config_value(player_config_df, ConfigKeys.STAT_NAME, ConfigKeys.STAT_ATK, ConfigKeys.STAT_NAME),
            initial_value=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_ATK, ConfigKeys.STAT_INITIAL_VALUE),
            meta_bonus_base=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_ATK, ConfigKeys.STAT_META_BONUS_BASE),
            meta_bonus_exp=get_config_value(player_config_df,ConfigKeys.STAT_NAME, ConfigKeys.STAT_ATK, ConfigKeys.STAT_META_BONUS_EXP),
            meta_cost_base=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_ATK, ConfigKeys.STAT_META_COST_BASE)),
            meta_cost_exp=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_ATK, ConfigKeys.STAT_META_COST_EXP)),
            level=0
        )
        stat_def = Meta_stat(
            name=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_DEF, ConfigKeys.STAT_NAME),
            initial_value=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_DEF, ConfigKeys.STAT_INITIAL_VALUE),
            meta_bonus_base=get_config_value(player_config_df,ConfigKeys.STAT_NAME, ConfigKeys.STAT_DEF, ConfigKeys.STAT_META_BONUS_BASE),
            meta_bonus_exp=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_DEF, ConfigKeys.STAT_META_BONUS_EXP),
            meta_cost_base=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_DEF, ConfigKeys.STAT_META_COST_BASE)),
            meta_cost_exp=int(get_config_value(player_config_df,ConfigKeys.STAT_NAME, ConfigKeys.STAT_DEF, ConfigKeys.STAT_META_COST_EXP)),
            level=0
        )
        stat_max_hp = Meta_stat(
            name=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_NAME),
            initial_value=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_INITIAL_VALUE),
            meta_bonus_base=get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_META_BONUS_BASE),
            meta_bonus_exp=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_META_BONUS_EXP)),
            meta_cost_base=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_META_COST_BASE)),
            meta_cost_exp=int(get_config_value(player_config_df, ConfigKeys.STAT_NAME,ConfigKeys.STAT_MAX_HP, ConfigKeys.STAT_META_COST_EXP)),
            level=0
        )       
        gold = 0
        chapter = 1

        new_meta = Player_meta_progression(
            log=log,
            stat_atk=stat_atk,
            stat_def=stat_def,
            stat_max_hp=stat_max_hp,
            gold=gold,
            chapter_level=chapter
        ) 

        return new_meta

    def add_gold(self, value:int):
        self.gold+= value
        return
    
    def get_cheapest_stat(self) -> Meta_stat:
        stats = [self.stat_atk, self.stat_def, self.stat_max_hp]
        return min(stats, key=lambda stat: stat.get_cost())
    
    def simulate(self):
    #get cheapest stat to upgrade
        stat = self.get_cheapest_stat()

        if self.gold >= stat.get_cost():
            self.gold -= stat.get_cost()
            stat.level_up()
            self.log.add_log(
                Log_Actor.SIMULATION, Log_Granularity.META, Log_Action.SIMULATE,
                f"Upgraded {stat.name} to level {stat.get_level()}",
                {
                    "stat_name": stat.name,
                    "new_level": stat.get_level(),
                    "new_value": stat.get_value(),
                    "remaining_gold": self.gold
                }
            )

        return

    def chapter_level_up(self):
        self.chapter_level += 1
        self.log.add_log(
            Log_Actor.SIMULATION, Log_Granularity.META, Log_Action.SIMULATE,
            f"Chapter level up: new chapter level is {self.chapter_level}",
            {"chapter_level": self.chapter_level}
        )
        return

@dataclass
class Player_Character:

    log: Log

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

    def modify_max_hp(self, value: int):
         self.stat_max_hp+=value

    def is_dead(self) -> bool:
        return self.stat_hp <= 0
    
    @staticmethod
    def initialize(stat_atk: int, stat_def:int, stat_max_hp:int, log:Log) -> 'Player_Character':
        new_character =Player_Character(
            log=log,
            stat_atk=stat_atk,
            stat_def=stat_def,
            stat_hp = stat_max_hp,
            stat_max_hp=stat_max_hp
        )

        return new_character

@dataclass
class EnemyCharacter:

    class Enemy_Types (Enum):
        SLIME = "slime"
        SKELETON = "skeleton"
        BOSS = "boss"

    log:Log
   
    type: Enemy_Types
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
    
    @staticmethod
    def initialize(enemies_config, enemy_type: Enemy_Types, log: Log) -> 'EnemyCharacter':

        new_enemy = EnemyCharacter(
            log=log,
            type = enemy_type,
            stat_atk= get_config_value_str_row(enemies_config, ConfigKeys.ENEMY_TYPE, enemy_type.value, ConfigKeys.ENEMY_ATK),
            stat_def= get_config_value_str_row(enemies_config, ConfigKeys.ENEMY_TYPE, enemy_type.value, ConfigKeys.ENEMY_DEF),
            stat_max_hp= get_config_value_str_row(enemies_config, ConfigKeys.ENEMY_TYPE, enemy_type.value, ConfigKeys.ENEMY_MAX_HP),
            stat_hp= get_config_value_str_row(enemies_config, ConfigKeys.ENEMY_TYPE, enemy_type.value, ConfigKeys.ENEMY_MAX_HP)
        )

        return new_enemy

@dataclass
class Day:

    class EventType(Enum):
        INCREASE_ATK = "increase_atk"
        INCREASE_DEF = "increase_def"
        INCREASE_MAX_HP = "increase_max_hp"
        RESTORE_HP = "restore_hp"
        BATTLE = "battle"    
    log: Log
    chapter_num: int
    day_num: int
    event_type: EventType
    event_param: Any
    gold_reward: int
    event_enemy: Optional[EnemyCharacter]

    @staticmethod
    def initialize(day_config, enemies_config, log: Log) -> 'Day':
        event_name = day_config[ConfigKeys.CHAPTER_DAILY_EVENT.value]
        event_type = Day.EventType(event_name)
        event_param = day_config[ConfigKeys.CHAPTER_DAILY_EVENT_PARAM.value]
        gold_reward = int(day_config[ConfigKeys.CHAPTER_DAILY_GOLD_REWARD.value]) 
        chapter_num = int(day_config[ConfigKeys.CHAPTER_NUM.value])
        day_num = int(day_config[ConfigKeys.CHAPTER_DAY_NUM.value])

        # Convert event_param to int for numeric operations
        if event_type in [Day.EventType.INCREASE_ATK, Day.EventType.INCREASE_DEF, 
                      Day.EventType.INCREASE_MAX_HP, Day.EventType.RESTORE_HP]:
            event_param = int(event_param)

        enemy_type = None
        if event_type == Day.EventType.BATTLE:
            enemy_type = EnemyCharacter.Enemy_Types(event_param) 

        new_day =  Day(
            log=log,
            chapter_num=chapter_num,
            day_num=day_num,
            event_type=event_type,
            event_param=event_param,
            gold_reward=gold_reward,
            event_enemy=EnemyCharacter.initialize(
                enemies_config,
                enemy_type,
                log
            ) if enemy_type else None
        )   

        return new_day

    def simulate(self, player_character: Player_Character, meta_progression: Player_meta_progression):

        match self.event_type:
            case Day.EventType.INCREASE_ATK:
                player_character.modify_atk(self.event_param)
                meta_progression.add_gold(self.gold_reward)
            case Day.EventType.INCREASE_DEF:
                player_character.modify_def(self.event_param)
                meta_progression.add_gold(self.gold_reward)
            case Day.EventType.INCREASE_MAX_HP:
                player_character.modify_max_hp(self.event_param)
                meta_progression.add_gold(self.gold_reward)
            case Day.EventType.RESTORE_HP:
                player_character.modify_hp(self.event_param)
                meta_progression.add_gold(self.gold_reward)
            case Day.EventType.BATTLE:
                if self.event_enemy is None:
                    raise ValueError("Battle event requires an enemy character.")
                simulate_battle(player_character, self.event_enemy, self.log)
                if(not player_character.is_dead()):
                    meta_progression.add_gold(self.gold_reward)
            case _:
                raise ValueError(f"Unknown event type: {self._event_type}")

        self.log.add_log(
            Log_Actor.SIMULATION, Log_Granularity.DAY, Log_Action.SIMULATE,
            f"Day simulated with event {self.event_type.value} and param {self.event_param}",
            {
            }
        )

        return


@dataclass
class Chapter:

    log: Log

    days: List[Day]
    player_character: Player_Character
    meta_progression: Player_meta_progression

    @staticmethod
    def initialize(chapter_config_df, meta_progression: Player_meta_progression, enemies_config_df, log: Log) -> 'Chapter':

        #Instantiate the player characteer
        player_character = Player_Character.initialize(
            meta_progression.stat_atk.get_value(),
            meta_progression.stat_def.get_value(),
            meta_progression.stat_max_hp.get_value(),
            log=log
            )    
        
        #Instantiate the day list with all the events
        days: List[Day] = []
        for index,day_config in chapter_config_df.iterrows():
            new_day = Day.initialize(day_config, enemies_config_df, log)
            days.append(new_day)
    
        #Create the new chapter
        chapter = Chapter(
            log,
            days,
            player_character,
            meta_progression)
        
        return chapter


    def simulate(self) -> bool:

        victory = True

        for day in self.days:
            day.simulate(self.player_character, self.meta_progression)
            if(self.player_character.is_dead()):
                victory = False
                break

        self.log.add_log(
            Log_Actor.SIMULATION, Log_Granularity.CHAPTER, Log_Action.SIMULATE,
            f"Chapter {self.meta_progression.chapter_level} simulation completed with status: {'Victory' if victory else 'Defeat'}",
            {
                "chapter_level": self.meta_progression.chapter_level,
                "victory": victory
            }
        )

        return victory

def get_config_value(config_df, row: ConfigKeys, row_key: ConfigKeys, column_key: ConfigKeys) -> Any:
    return config_df.loc[config_df[row.value] == row_key.value, column_key.value].iloc[0]

def get_config_value_str_row(config_df, row: ConfigKeys, row_key: str, column_key: ConfigKeys) -> Any:
    return config_df.loc[config_df[row.value] == row_key, column_key.value].iloc[0]

def simulate_battle(player_character: Player_Character, enemy: EnemyCharacter, log: Log):

    log.add_log(
        Log_Actor.GAME,
        Log_Granularity.BATTLE,
        Log_Action.INITIALIZE, 
        f"Battle initialized between player and {enemy.type.value}",
        {
        }
    )

    while not player_character.is_dead() and not enemy.is_dead():
        # Player attacks enemy
        damage_to_enemy = max(0, player_character.stat_atk - enemy.stat_def)
        enemy.modify_hp(-damage_to_enemy)

        log.add_log(
            Log_Actor.GAME, Log_Granularity.TURN, Log_Action.PLAYER_ATTACK,
            f"Player attacks {enemy.type.value} for {damage_to_enemy} damage. Enemy HP: {enemy.stat_hp}/{enemy.stat_max_hp}",
            {
             "damage": damage_to_enemy
            })

        if enemy.is_dead():
            log.add_log(
                Log_Actor.GAME, Log_Granularity.BATTLE, Log_Action.ENEMY_DEFEATED,
                f"Enemy {enemy.type.value} defeated!",
                {
                }
            )
            break

        # Enemy attacks player
        damage_to_player = max(0, enemy.stat_atk - player_character.stat_def)
        player_character.modify_hp(-damage_to_player)

        log.add_log(
            Log_Actor.GAME, Log_Granularity.TURN, Log_Action.ENEMY_ATTACK,
            f"{enemy.type.value} attacks player for {damage_to_player} damage. Player HP: {player_character.stat_hp}/{player_character.stat_max_hp}",
            {"damage": damage_to_player})

        if player_character.is_dead():

            log.add_log(
                Log_Actor.GAME, Log_Granularity.BATTLE, Log_Action.PLAYER_DEFEATED,
                "Player defeated!",
                {
                }
            )
            break

        assert damage_to_enemy == 0 and damage_to_player == 0, "Infinite battle detected, both 0 damage"
    

    return


@dataclass
class Model:
    log: Log
    config: Config
    

    @staticmethod
    def initialize(config: Config) -> 'Model':
        log = Log.initialize()
        return Model(log=log, config=config)

    def simulate(self)-> Log:

        

        player_config = self.config.get_player_config()
        enemies_config = self.config.get_enemies_config()
        total_chapters = self.config.get_total_chapters()

        self.log.add_log(
            Log_Actor.SIMULATION, Log_Granularity.SIMULATION, Log_Action.INITIALIZE,
            "Model initialized configs: player and enemies",
            {"player_config": player_config,
                "enemies_config": enemies_config,
                "total_chapters": total_chapters})

        meta_progression = Player_meta_progression.initialize(player_config, self.log)

        rounds_done = 0
        max_allowed_rounds = 5 #TODO: Turn into config value

        # Chapters Sequence Loop
        while(rounds_done<=max_allowed_rounds and meta_progression.chapter_level<=total_chapters):
            rounds_done+=1

            assert rounds_done <= 10, "possible infinite loop detected"

            self.log.add_log(
                Log_Actor.SIMULATION, Log_Granularity.CHAPTER, Log_Action.SIMULATE,
                f"Starting simulation for chapter {meta_progression.chapter_level} in round {rounds_done}",
                {"chapter_level": meta_progression.chapter_level,
                    "rounds_done": rounds_done
                    })
            
            # Chapter Simulation
            chapter_level = meta_progression.chapter_level
            chapter_config = self.config.get_chapter_config(chapter_level)
            chapter = Chapter.initialize(chapter_config, meta_progression, enemies_config, self.log)
            victory_bool = chapter.simulate()

            # Chapter Simulation
            self.log.add_log(
                Log_Actor.SIMULATION, Log_Granularity.CHAPTER, Log_Action.SIMULATE,
                f"Chapter {chapter_level} simulation in round {rounds_done} completed with status: {'Victory' if victory_bool else 'Defeat'}",
                {"chapter_level": chapter_level,
                    "victory": victory_bool}
            )

            # Meta Progression Simulation
            meta_progression.simulate()
            
            if victory_bool:
                meta_progression.chapter_level += 1 

        return self.log
                

    
