import streamlit as st, time, os
import pandas as pd
from config_import import Config, ConfigKeys
from model import Model
import matplotlib.pyplot as plt
from typing import Any, Dict, cast
from auxiliar import Log
import debugpy


def show_log_table(log_df: pd.DataFrame):
    # Augmentar amplada de taula
    st.markdown("""
        <style>
        .stDataFrame div[data-testid="stHorizontalBlock"] {
            overflow-x: auto;
        }
        .stDataFrame table {
            width: 100% !important;
        }
        .stDataFrame td {
            white-space: pre-wrap;
            max-width: 400px;
        }
        .stDataFrame th {
            position: sticky;
            top: 0;
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Filtres dinàmics
    actor_options = log_df["actor"].unique().tolist()
    granularity_options = log_df["granularity"].unique().tolist()
    action_options = log_df["action"].unique().tolist()

    selected_actor = st.multiselect("Filter by Actor", actor_options,default=[])
    selected_granularity = st.multiselect("Filter by Granularity", granularity_options, default=[])
    default_actions = [a for a in action_options if a != "initialize"]
    selected_action = st.multiselect("Filter by Action", action_options, default=default_actions)

    filtered_df = log_df.copy()
    if selected_actor:
        filtered_df = filtered_df[filtered_df["actor"].isin(selected_actor)]
    if selected_granularity:
        filtered_df = filtered_df[filtered_df["granularity"].isin(selected_granularity)]
    if selected_action:
        filtered_df = filtered_df[filtered_df["action"].isin(selected_action)]

    # Eliminar columnes 'index' i 'payload' si existeixen
    #filtered_df = filtered_df.drop(columns=["index", "payload"], errors="ignore")

    # Mostrar taula final
    st.dataframe(filtered_df[["actor", "granularity","action","message"]], hide_index=True, use_container_width=True ,height=700)

    """"
    where day and simulate, get payload -> day and player_character"""

    daily_graph_df = filtered_df[
        (filtered_df["granularity"] == "day") & (filtered_df["action"] == "simulate")
    ]
    st.dataframe(daily_graph_df)

st.write("Run nº", os.getpid(), time.time())

st.title("Capybara Go Inspired Simulator")

config = Config.initialize()

# Display the config to allow editing
st.subheader("Config Editor")
edited_player_config = st.data_editor(config.get_player_config())
edited_enemies_config = st.data_editor(config.get_enemies_config())
edited_chapters_config = st.data_editor(config.get_all_chapters_config())
edited_player_behavior_config = st.data_editor(config.get_player_behavior_config())
edited_action_time_costs_config = st.data_editor(config.get_timers_config())

# Simulation
if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False

if st.button("Run Simulation"):

    config.reasign_config(
        new_player_config=edited_player_config,
        new_enemies_config=edited_enemies_config,
        new_chapters_config=edited_chapters_config,
        new_player_behavior_config=edited_player_behavior_config,
        new_action_time_costs_df=edited_action_time_costs_config
    )

    model = Model.initialize(config)
    log = model.simulate()
    log_df = log.get_logs_as_dataframe()
    st.dataframe(log_df)

    log_df[log_df["action"] == Log.Action.ROUND_COMPLETED.value]

    st.line_chart(
        log_df[log_df["action"] == Log.Action.ROUND_COMPLETED.value].set_index("rounds_done")["chapter_level"],
        use_container_width=True,
        x_label="Rounds Done",
        y_label="Chapter Level"
    )



    #st.session_state.simulation_done = True

    # Show results
    #if st.session_state.simulation_done:
        #log_df = Logger.get_logs_as_dataframe()
        #show_log_table(log_df)
        #st.write(log_df)
        #plot_test()
        #plot_turn_stats(log)

    
    
    

