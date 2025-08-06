import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import json
from typing import Optional
from enum import Enum
from dataclasses import dataclass, field

class ConfigSheets(Enum):
    SPREADSHEET_NAME = "capybara_sim_data"
    PLAYER_SHEET_NAME = "PLAYER"
    ENEMIES_SHEET_NAME = "ENEMIES"
    CHAPTERS_SHEET_NAME = "CHAPTERS"
    PLAYER_BEHAVIOR_SHEET_NAME = "PLAYER_BEHAVIOR"
    TIMERS_SHEET_NAME = "TIMERS"

class ConfigKeys(Enum):
    STAT_NAME = "stat_name"
    STAT_INITIAL_VALUE = "stat_initial_value"
    STAT_META_BONUS_BASE = "stat_meta_bonus_base"
    STAT_META_BONUS_EXP = "stat_meta_bonus_exp"
    STAT_META_COST_BASE = "stat_meta_cost_base"
    STAT_META_COST_EXP = "stat_meta_cost_exp"
    STAT_ATK = "atk"
    STAT_DEF = "def"
    STAT_MAX_HP = "max_hp"
    ENEMY_TYPE = "enemy_type"
    ENEMY_ATK = "enemy_atk"
    ENEMY_DEF = "enemy_def"
    ENEMY_MAX_HP = "enemy_max_hp"
    CHAPTER_NUM = "chapter_num"
    CHAPTER_DAY_NUM = "day_num"
    CHAPTER_DAILY_EVENT = "daily_event"
    CHAPTER_DAILY_EVENT_PARAM = "daily_event_param"
    CHAPTER_DAILY_GOLD_REWARD = "gold_reward"
    PLAYER_BEHAVIOR_PLAYER_TYPE = "player_type"
    PLAYER_BEHAVIOR_SIMULATE = "simulate"
    PLAYER_BEHAVIOR_SESSIONS_PER_DAY = "sessions_per_day"
    PLAYER_BEHAVIOR_SESSION_TIME = "session_time"
    TIMERS_ACTION_TYPE = "event_type"
    TIMERS_ACTION_TIME_COST = "event_time_cost"

class ConfigTimerActions(Enum): 
    EVENT_INCREASE_ATK = "increase_atk"
    EVENT_INCREASE_DEF = "increase_def"
    EVENT_INCREASE_MAX_HP = "increase_max_hp"
    EVENT_RESTORE_HP = "restore_hp"
    BATTLE_ENEMY_TURN = "battle_enemy_turn"
    BATTLE_PLAYER_TURN = "battle_player_turn"
    META_PROGRESSION = "meta_progression"


@st.cache_data(ttl=300)  # cache for 5 minutes
def _fetch_worksheet_df(spreadsheet_name: str, worksheet_name: str) -> pd.DataFrame:
    """
    Return the worksheet as DataFrame, caching the result to spare Google API calls.
    Parameters
    """
    client = connect_to_API()
    sheet = client.open(spreadsheet_name)
    return pd.DataFrame(sheet.worksheet(worksheet_name).get_all_records())

@dataclass
class Config:

    _player_config_df: pd.DataFrame
    _enemies_config_df: pd.DataFrame
    _chapters_config_df: pd.DataFrame
    _player_behavior_config_df: pd.DataFrame
    _action_time_costs_df: pd.DataFrame


    @staticmethod
    def initialize() -> 'Config':
        # Connect to Google Sheets
        client = connect_to_API()

        # Get the spreadsheet and turn into DataFrames
        sheet = client.open(ConfigSheets.SPREADSHEET_NAME.value)
  
        player_config_df = _fetch_worksheet_df( ConfigSheets.SPREADSHEET_NAME.value, ConfigSheets.PLAYER_SHEET_NAME.value)
        enemies_config_df = _fetch_worksheet_df(ConfigSheets.SPREADSHEET_NAME.value, ConfigSheets.ENEMIES_SHEET_NAME.value)
        chapters_config_df = _fetch_worksheet_df(ConfigSheets.SPREADSHEET_NAME.value, ConfigSheets.CHAPTERS_SHEET_NAME.value )
        player_behavior_config_df = _fetch_worksheet_df(ConfigSheets.SPREADSHEET_NAME.value, ConfigSheets.PLAYER_BEHAVIOR_SHEET_NAME.value)
        action_timers_df = _fetch_worksheet_df(ConfigSheets.SPREADSHEET_NAME.value, ConfigSheets.TIMERS_SHEET_NAME.value)

        config = Config(
            _player_config_df=player_config_df,
            _enemies_config_df=enemies_config_df,
            _chapters_config_df=chapters_config_df,
            _player_behavior_config_df=player_behavior_config_df,
            _action_time_costs_df=action_timers_df
        )

        return config
    
        
    def get_total_chapters(self) -> int:
        return self._chapters_config_df['chapter_num'].max()

    def get_chapter_config(self, chapter_number: int) -> pd.DataFrame:
        return self._chapters_config_df[self._chapters_config_df['chapter_num'] == chapter_number].copy()

    def get_all_chapters_config(self) -> pd.DataFrame:
        return self._chapters_config_df

    def get_player_config(self) -> pd.DataFrame:
        return self._player_config_df
    
    def get_enemies_config(self) -> pd.DataFrame:
        return self._enemies_config_df
    
    def get_player_behavior_config(self) -> pd.DataFrame:
        return self._player_behavior_config_df
    
    def get_timers_config(self) -> pd.DataFrame:
        return self._action_time_costs_df

    def reasign_config(self, new_player_config, new_enemies_config, new_chapters_config, new_player_behavior_config, new_action_time_costs_df):
        self._player_config_df = new_player_config
        self._enemies_config_df = new_enemies_config
        self._chapters_config_df = new_chapters_config
        self._player_behavior_config_df = new_player_behavior_config
        self._action_time_costs_df = new_action_time_costs_df


def connect_to_API() -> gspread.Client:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    service_account_info = st.secrets["gcp"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(creds)
    return client