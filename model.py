from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
import config_import as config_import
from config_import import ConfigKeys, Config, ConfigTimerActions
from enum import Enum
from utils import Log, Timer

# Controls the time the players spends in the game
@dataclass
class PlayerBehavior:
    log: Log
    timer: Timer
    timers_config: pd.DataFrame

    player_session_time: float
    player_sessions_per_day: int
    
    @staticmethod
    def initialize(player_behavior_config: pd.DataFrame, timers_config: pd.DataFrame, log:Log, timer: Timer) -> 'PlayerBehavior':

        selected_player_behavior = player_behavior_config[player_behavior_config[ConfigKeys.PLAYER_BEHAVIOR_SIMULATE.value] == "TRUE"].iloc[0]
        player_session_time = float(selected_player_behavior.loc[ConfigKeys.PLAYER_BEHAVIOR_SESSION_TIME.value])
        player_sessions_per_day = int(selected_player_behavior.loc[ConfigKeys.PLAYER_BEHAVIOR_SESSIONS_PER_DAY.value])

        return PlayerBehavior(
            log=log,
            timer=timer,
            player_session_time=player_session_time,
            player_sessions_per_day=player_sessions_per_day,
            timers_config=timers_config,
        )

    def check_session(self):

        # If session time > player behavior session, start a new session
        # If session number > player behavior sessions per day, pass a day
        if self.timer.get_session_time() > self.player_session_time:
            
            if self.timer.get_day_session() >= self.player_sessions_per_day:
                self.timer.set_new_day()
                self.log.log_player_new_day(
                    self.timer.get_day())  
            else:
                self.timer.set_new_session()
                self.log.log_player_new_session(
                    session_num=self.timer.get_day_session(),
                    day_num=self.timer.get_day())
                
        return
    
    def time_spent(self, time: float):
        self.timer.set_time_increment(time)
        self.check_session()
        return


# -----------------------------
#     Meta Progression Classes
# -----------------------------

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
    player_behavior: PlayerBehavior
    action_time_costs: Dict[str, float]

    stat_atk: Meta_stat
    stat_def: Meta_stat
    stat_max_hp: Meta_stat
    
    gold: int = 0
    chapter_level: int = 0


    @staticmethod
    def initialize(player_config_df, log: Log, player_behavior: PlayerBehavior, action_time_costs: Dict[str, float]) -> 'Player_meta_progression':
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
            player_behavior=player_behavior,
            action_time_costs=action_time_costs,
            stat_atk=stat_atk,
            stat_def=stat_def,
            stat_max_hp=stat_max_hp,
            gold=gold,
            chapter_level=chapter,
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
            self.log.log_stat_level_up(stat.name, stat.get_level())

        self.player_behavior.time_spent(self.action_time_costs[ConfigTimerActions.META_PROGRESSION.value])

        return

    def chapter_level_up(self):
        self.chapter_level += 1
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
    playerbehavior: PlayerBehavior
    action_time_costs: Dict[str, float]
    chapter_num: int
    day_num: int
    event_type: EventType
    event_param: Any
    gold_reward: int
    event_enemy: Optional[EnemyCharacter]

    @staticmethod
    def initialize(day_config, enemies_config, log: Log, playerbehavior: PlayerBehavior, action_time_costs: Dict[str, float]) -> 'Day':
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
            playerbehavior=playerbehavior,
            action_time_costs=action_time_costs,
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

        self.log.log_chapter_run_day_completed(
            chapter_num=self.chapter_num,
            day_num=self.day_num,
            event_type=self.event_type.value,
            event_param=self.event_param,
            player_hp=player_character.stat_hp,
            player_max_hp=player_character.stat_max_hp,
            player_atk=player_character.stat_atk,
            player_def=player_character.stat_def
        )
        
        match self.event_type:
            case Day.EventType.INCREASE_ATK:
                player_character.modify_atk(self.event_param)
                meta_progression.add_gold(self.gold_reward)
                self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.EVENT_INCREASE_ATK.value])
            case Day.EventType.INCREASE_DEF:
                player_character.modify_def(self.event_param)
                meta_progression.add_gold(self.gold_reward)
                self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.EVENT_INCREASE_DEF.value])
            case Day.EventType.INCREASE_MAX_HP:
                player_character.modify_max_hp(self.event_param)
                meta_progression.add_gold(self.gold_reward)
                self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.EVENT_INCREASE_MAX_HP.value])
            case Day.EventType.RESTORE_HP:
                player_character.modify_hp(self.event_param)
                meta_progression.add_gold(self.gold_reward)
                self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.EVENT_RESTORE_HP.value])
            case Day.EventType.BATTLE:
                if self.event_enemy is None:
                    raise ValueError("Battle event requires an enemy character.")
                self.simulate_battle(player_character, self.event_enemy, self.log)
                if(not player_character.is_dead()):
                    meta_progression.add_gold(self.gold_reward)
            case _:
                raise ValueError(f"Unknown event type: {self._event_type}")

        return

    def simulate_battle(self, player_character: Player_Character, enemy: EnemyCharacter, log: Log):

        while not player_character.is_dead() and not enemy.is_dead():
            # Player attacks enemy
            damage_to_enemy = max(0, player_character.stat_atk - enemy.stat_def)
            enemy.modify_hp(-damage_to_enemy)
            log.log_player_attack(
                enemy_type=enemy.type.value,
                damage=damage_to_enemy,
                enemy_hp=enemy.stat_hp
            )
            self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.BATTLE_PLAYER_TURN.value])

            if enemy.is_dead():

                log.log_battle_victory(
                    enemy_type=enemy.type.value,
                    player_hp=player_character.stat_hp
                )
                break

            # Enemy attacks player
            damage_to_player = max(0, enemy.stat_atk - player_character.stat_def)
            player_character.modify_hp(-damage_to_player)
            log.log_enemy_attack(
                enemy_type=enemy.type.value,
                damage=damage_to_player,
                player_hp=player_character.stat_hp
            )
            self.playerbehavior.time_spent(self.action_time_costs[ConfigTimerActions.BATTLE_ENEMY_TURN.value])

            if player_character.is_dead():

                log.log_battle_defeat(
                    enemy_type=enemy.type.value,
                    enemy_hp= enemy.stat_hp
                )

                break

            assert damage_to_enemy == 0 and damage_to_player == 0, "Infinite battle detected, both 0 damage"
        

        return


@dataclass
class Chapter:

    log: Log
    player_behavior: PlayerBehavior
    action_time_costs: Dict[str, float]

    days: List[Day]
    player_character: Player_Character
    meta_progression: Player_meta_progression

    @staticmethod
    def initialize(chapter_config_df, meta_progression: Player_meta_progression, enemies_config_df, log: Log, player_behavior: PlayerBehavior, action_time_costs: Dict[str, float]) -> 'Chapter':

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
            new_day = Day.initialize(day_config, enemies_config_df, log, player_behavior , action_time_costs)
            days.append(new_day)
    
        #Create the new chapter
        chapter = Chapter(
            log=log,
            player_behavior=player_behavior,
            action_time_costs=action_time_costs,
            days=days,
            player_character=player_character,
            meta_progression=meta_progression
        )

        return chapter


    def simulate(self) -> bool:

        victory = True

        for day in self.days:
            day.simulate(self.player_character, self.meta_progression)
            if(self.player_character.is_dead()):
                victory = False
                break

        if victory:
            self.log.log_chapter_victory(self.meta_progression.chapter_level)
        else:
            self.log.log_chapter_defeat(self.meta_progression.chapter_level)

        return victory

def get_config_value(config_df, row: ConfigKeys, row_key: ConfigKeys, column_key: ConfigKeys) -> Any:
    return config_df.loc[config_df[row.value] == row_key.value, column_key.value].iloc[0]

def get_config_value_str_row(config_df, row: ConfigKeys, row_key: str, column_key: ConfigKeys) -> Any:
    return config_df.loc[config_df[row.value] == row_key, column_key.value].iloc[0]



# -----------------------------
#   Meta Progression Classes
# -----------------------------


        
        
@dataclass
class Model:
    log: Log
    config: Config
    timer: Timer

    player_behavior: PlayerBehavior
    meta_progression: Player_meta_progression

    action_time_costs: Dict[str, float]


    @staticmethod
    def initialize(config: Config) -> 'Model':

        timer = Timer.initialize(config.get_player_behavior_config())
        log = Log.initialize(timer)
        player_behavior = PlayerBehavior.initialize(config.get_player_behavior_config(), config.get_timers_config(), log, timer)
        player_config = config.get_player_config()

        action_time_costs = {
            str(row[ConfigKeys.TIMERS_ACTION_TYPE.value]): float(row[ConfigKeys.TIMERS_ACTION_TIME_COST.value])
            for _, row in config.get_timers_config().iterrows()
        }

        meta_progression = Player_meta_progression.initialize(player_config, log, player_behavior, action_time_costs)

        

        return Model(
            log=log,
            config=config,
            timer=timer,
            player_behavior=player_behavior,
            meta_progression=meta_progression,
            action_time_costs=action_time_costs
        )

    def simulate(self)-> Log:
    
        enemies_config = self.config.get_enemies_config()
        total_chapters = self.config.get_total_chapters()

        rounds_done = 0

        while(self.meta_progression.chapter_level<=total_chapters):
            rounds_done+=1
            assert rounds_done < 1000, "Possible infinite loop detected"

            # Player Behavior Simulation
            #self.player_behavior.check_session()

            # Chapter Simulation
            chapter_level = self.meta_progression.chapter_level
            chapter_config = self.config.get_chapter_config(chapter_level)
            chapter = Chapter.initialize(chapter_config, self.meta_progression, enemies_config, self.log, self.player_behavior, self.action_time_costs)
            victory_bool = chapter.simulate()

            # Player Behavior Simulation
            #self.player_behavior.check_session()

            # Meta Progression Simulation
            self.meta_progression.simulate()

            self.log.log_round_completed(chapter_level, victory_bool, rounds_done)

            if victory_bool:
                self.meta_progression.chapter_level += 1

        return self.log
                

    
