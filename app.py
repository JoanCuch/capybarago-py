import streamlit as st
import pandas as pd
from config_import import  initialize_config
from model import model, Chapter_Log
import matplotlib.pyplot as plt

st.title("Capybara Go Simulator")
#st.sidebar.header("Config")
#st.sidebar.button("Reload Page", on_click=st.rerun())


config_df = initialize_config()

#st.write(config_df)
st.divider()
st.subheader("Chapter Daily Log")
chapters_log = model(config_df)

st.divider()

for chapter in chapters_log:
    #st.subheader(f"Chapter: {chapter.name}")
    st.dataframe(chapter.daily_log)

"""
log_df = pd.DataFrame(chapters_log[0].chapter_log.daily_log)

st.line_chart(
    log_df[["day", "player_atk", "player_def", "player_hp", "player_maxhp"]],
    x = "day",
    y = ["player_atk", "player_def", "player_hp", "player_maxhp"],
    x_label= "day",
    y_label= "player stats",
    color=["#000000", "#1982C4", "#FF595E", "#FFCA3A"]
)

st.line_chart(
    log_df[["day", "player_delta_atk", "player_delta_def", "player_delta_hp", "player_delta_maxhp"]],
    x = "day",
    y = ["player_delta_atk", "player_delta_def", "player_delta_hp", "player_delta_maxhp"],
    x_label= "day",
    y_label= "player stats",
    color=["#000000", "#1982C4", "#FF595E", "#FFCA3A"]
)
"""
