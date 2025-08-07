import streamlit as st, time, os
import pandas as pd
from config_import import Config, ConfigKeys
from model import Model
from typing import Any, Dict, cast
from auxiliar import Log


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


st.title("Capybara Go Simulator")

with st.sidebar:
    if st.button("Reset Config"):
        st.cache_data.clear()
        st.session_state.clear()

    st.sidebar.toggle("Show/Hide Config", key="modify_config")


if 'config' not in st.session_state:
    st.session_state.config = Config.initialize()

# Initialise storage for logs (only first run)
if 'log_df' not in st.session_state:
    st.session_state.log_df = None

if st.session_state.modify_config:
    modify_config()
    

player_type_select()

if st.button("Run Simulation"):
    # Run simulation once and store results
    st.session_state.model = Model.initialize(st.session_state.config)
    st.session_state.log = st.session_state.model.simulate()
    st.session_state.log_df = st.session_state.log.get_logs_as_dataframe()

    
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