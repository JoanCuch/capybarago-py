import streamlit as st, time, os
import pandas as pd
from config_import import Config, ConfigKeys
from model import Model
from typing import Any, Dict, cast
from utils import Log


def modify_config():
    with st.form("edit_config"):
        st.header("Config Modification")
        st.write("You can modify the configuration of the simulation here. Make sure to save your changes.")

        st.subheader("Player Behavior Config")
        edited_player_behavior_config = st.data_editor(st.session_state.config.get_player_behavior_config())
        st.subheader("Action Time Costs Config")
        edited_action_time_costs_config = st.data_editor(st.session_state.config.get_timers_config())
        st.subheader("Player Config")
        edited_player_config = st.data_editor(st.session_state.config.get_player_config())
        st.subheader("Enemies Config")
        edited_enemies_config = st.data_editor(st.session_state.config.get_enemies_config())
        st.subheader("Chapters Config")
        edited_chapters_config = st.data_editor(st.session_state.config.get_all_chapters_config())
        
        if st.form_submit_button('Submit my picks'):
            st.session_state.config.reasign_config(
                new_player_config=edited_player_config,
                new_enemies_config=edited_enemies_config,
                new_chapters_config=edited_chapters_config,
                new_player_behavior_config=edited_player_behavior_config,
                new_action_time_costs_df=edited_action_time_costs_config
            )
            st.write("Configuration updated successfully!")

def player_type_select():
    player_behavior_df = st.session_state.config.get_player_behavior_config()
    player_types = player_behavior_df["player_type"].tolist()
    selected_player_type = st.selectbox(
        "Select player type to simulate",
        player_types,
        key="player_type_select",
        index=0
    )
    # Set 'simulate' to string "TRUE"/"FALSE" as expected by the model
    simulate_col = ConfigKeys.PLAYER_BEHAVIOR_SIMULATE.value
    player_behavior_df[simulate_col] = player_behavior_df["player_type"].apply(
        lambda x: "TRUE" if x == selected_player_type else "FALSE"
    )

    st.write("Selected Player Type:", selected_player_type)
    st.write("Session per Day: ", player_behavior_df[player_behavior_df["player_type"] == selected_player_type][ConfigKeys.PLAYER_BEHAVIOR_SESSIONS_PER_DAY.value].values[0])
    st.write("Session Duration: ", player_behavior_df[player_behavior_df["player_type"] == selected_player_type][ConfigKeys.PLAYER_BEHAVIOR_SESSION_TIME.value].values[0])

def print_charts_day_completion(log: pd.DataFrame):

    day_log = log[log["action"] == Log.Action.DAY_COMPLETED.value]

    #day_log = day_log[day_log["chapter"] == 1]

    day_log["chapter_day"] = (
        day_log["chapter"].astype(int).astype(str).str.zfill(2) + "_" +
        day_log["day"].astype(int).astype(str).str.zfill(2)
        )
    #day_log.set_index("chapter_day", inplace=True)
    day_log = day_log.sort_values(by=["chapter", "day"])
    #day_log.set_index("chapter_day", inplace=True)
    
    st.subheader("Player Stats Progression per Chapter Run")
    st.line_chart(
        x="chapter_day",
        y=["player_hp", "player_max_hp", "player_atk", "player_def"],
        data=day_log,
        use_container_width=True,
        x_label="Chapter Day",
        y_label="Session Stats",
    )

    return

def print_charts_chapter_day_progression(main_log: pd.DataFrame):

    log = main_log[main_log["action"] == Log.Action.CHAPTER_VICTORY.value]  

    # Create a DataFrame with minimum timer_day per chapter (first victory day)
    victory_log = log.groupby('chapter')['timer_day'].min().reset_index()
    
    chapter_tries = log.groupby('chapter')['chapter_run_try'].max().reset_index()
    victory_log = victory_log.merge(chapter_tries, on='chapter', how='left')
        
    st.subheader("Day Victory per Chapter")
    st.line_chart(
        victory_log.set_index('chapter')[['timer_day', 'chapter_run_try']],
        use_container_width=True,
        x_label="Chapter",
        y_label="Days to Complete"
    )

    # "timer_day": self.timer.get_day(),
    #         "timer_day_session": self.timer.get_day_session(),
    #         "timer_session_time": self.timer.get_session_time(),
    #         "action": self.Action.CHAPTER_VICTORY.value,
    #         "message": f"Chapter {chapter_num} completed with victory",
    #         "chapter": chapter_num

    return

def print_charts_combat_turns(main_log: pd.DataFrame):

    log = main_log[main_log["action"].isin([Log.Action.PLAYER_ATTACK.value, Log.Action.ENEMY_ATTACK.value])]

    log = log[log["chapter"] == 1]
    log["chapter_try_day_round"] = (
        log["chapter"].astype(int).astype(str).str.zfill(2) + "_" +
        log["chapter_run_try"].astype(int).astype(str).str.zfill(2) + "_" +
        log["day"].astype(int).astype(str).str.zfill(2) + "_" +
        log["combat_round"].astype(int).astype(str).str.zfill(2)
        )
    
    log = log.sort_values(by="chapter_try_day_round")

    st.line_chart(
        x="chapter_try_day_round",
        y=["player_hp", "enemy_hp"],
        data=log,
        use_container_width=True,
        x_label="Round",
        y_label="HP",
    )

    #     def log_player_attack(self,damage: int, enemy_type: str, enemy_hp: int):
    #     log_entry = {
    #         "day": self.timer.get_day(),
    #         "day_session": self.timer.get_day_session(),
    #         "session_time": self.timer.get_session_time(),
    #         "action": self.Action.PLAYER_ATTACK.value,
    #         "message": f"Player attacked {enemy_type} for {damage} damage",
    #         "damage": damage,
    #         "enemy_type": enemy_type,
    #         "enemy_hp": enemy_hp
    #     }
    #     self.logs.append(log_entry)

    # def log_enemy_attack(self, damage: int, enemy_type: str, player_hp: int, enemy_hp: int):
    #     log_entry = {
    #         "day": self.timer.get_day(),
    #         "day_session": self.timer.get_day_session(),
    #         "session_time": self.timer.get_session_time(),
    #         "action": self.Action.ENEMY_ATTACK.value,
    #         "message": f"{enemy_type} attacked player for {damage} damage",
    #         "enemy_damage": damage,
    #         "player_hp": player_hp,
    #         "enemy_hp": enemy_hp,
    #         "enemy_type": enemy_type
    #     }


    return

st.title("Capybara Go Simulator")

with st.sidebar:
    if st.button("Reset Config"):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

    st.sidebar.toggle("Show/Hide Config", key="modify_config")

    if st.button("Run Simulation"):
        st.session_state.model = Model.initialize(st.session_state.config)
        st.session_state.log = st.session_state.model.simulate()
        st.session_state.log_df = st.session_state.log.get_logs_as_dataframe()


if 'config' not in st.session_state:
    st.session_state.config = Config.initialize()

# Initialise storage for logs (only first run)
if 'log_df' not in st.session_state:
    st.session_state.log_df = None

if st.session_state.modify_config:
    modify_config()
    

player_type_select()

    
if st.session_state.log_df is not None:
    log_df = st.session_state.log_df

    # st.line_chart(
    #     log_df[log_df["action"] == Log.Action.ROUND_COMPLETED.value]
    #         .set_index("rounds_done")["chapter_level"],
    #     use_container_width=True,
    #     x_label="Rounds Done",
    #     y_label="Chapter Level"
    # )

    action_options = log_df["action"].unique().tolist()
    selected_actions = st.multiselect(
        "Select Actions",
        action_options,
        default=action_options,
        key="action_multiselect"
    )

    filtered_df = log_df[log_df["action"].isin(selected_actions)]
    st.dataframe(filtered_df, hide_index=True, height=700)


    print_charts_day_completion(log_df)
    print_charts_combat_turns(log_df)
    print_charts_chapter_day_progression(log_df)