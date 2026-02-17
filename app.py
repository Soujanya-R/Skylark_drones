import streamlit as st
import pandas as pd
from sheet_utils import connect_sheet, load_data
from logic import *

st.set_page_config(page_title="Skylark Drone Coordinator", layout="wide")
st.title("🚁 Skylark Drone Coordinator")


sheet = connect_sheet("Skylark Drones")
pilots_df, pilot_ws = load_data(sheet, "Pilot_Roster")
missions_df, mission_ws = load_data(sheet, "Missions")
drones_df, drone_ws = load_data(sheet, "Drone_Fleet")


option = st.sidebar.selectbox(
    "Choose Action",
    [
        "Show Available Pilots",
        "Assign Pilot to Mission",
        "Mark Pilot On Leave",
        "View Drone Fleet"
    ]
)

if option == "Show Available Pilots":
    st.subheader("Available Pilots")
    available = find_available_pilots(pilots_df)
    if available.empty:
        st.warning("No pilots available.")
    else:
        st.dataframe(available)

elif option == "Mark Pilot On Leave":
    st.subheader("Mark Pilot On Leave")
    pilot_name = st.selectbox("Select Pilot", pilots_df["name"])
    if st.button("Update Status"):
        row_index = pilots_df[pilots_df["name"] == pilot_name].index[0]
        pilots_df.loc[row_index, "status"] = "On Leave"
        pilot_ws.update([pilots_df.columns.values.tolist()] + pilots_df.values.tolist())
        st.success(f"{pilot_name} marked as On Leave.")


elif option == "Assign Pilot to Mission":
    st.subheader("Assign Pilot to Mission")
    mission_id = st.selectbox("Select Mission", missions_df["project_id"])

    if st.button("Find Smart Matches"):
        mission_row = missions_df[missions_df["project_id"] == mission_id]
        if mission_row.empty:
            st.error("Mission not found.")
        else:
            mission = mission_row.iloc[0]
            matches, warnings = match_pilots_to_mission(pilots_df, mission)

            if not matches:
                st.warning("No fully suitable pilots found.")
                st.write("⚠ Potential Pilot Mismatches:")

                candidates, drones, drone_warnings = urgent_reassignment_to_mission(pilots_df, drones_df, mission)

                if candidates:
                    st.write("🔄 Urgent Reassignment Candidates:")
                    st.dataframe(pd.DataFrame(candidates))

                    selected_pilot = st.selectbox(
                        "Select Pilot for Urgent Reassignment",
                        [c["Pilot"] for c in candidates]
                    )

                    if st.button("Confirm Urgent Assignment"):
                        row_index = pilots_df[pilots_df["name"] == selected_pilot].index[0]
                        pilots_df.loc[row_index, "status"] = "Assigned"
                        pilots_df.loc[row_index, "current_assignment"] = mission_id
                        pilot_ws.update([pilots_df.columns.values.tolist()] + pilots_df.values.tolist())
                        st.success(f"{selected_pilot} urgently assigned to {mission_id}.")

                        if drones:
                            st.success("Compatible drones available:")
                            st.dataframe(pd.DataFrame(drones))
                        if drone_warnings:
                            st.warning("Drone Warnings:")
                            st.dataframe(pd.DataFrame(drone_warnings))
                else:
                    st.warning("No candidates available for urgent reassignment.")
            else:
                st.success("Suitable Pilots Found:")
                st.dataframe(pd.DataFrame(matches))

                selected_name = st.selectbox("Select Pilot to Assign", [m["name"] for m in matches])
                if st.button("Confirm Assignment"):
                    row_index = pilots_df[pilots_df["name"] == selected_name].index[0]
                    pilots_df.loc[row_index, "status"] = "Assigned"
                    pilots_df.loc[row_index, "current_assignment"] = mission_id
                    pilot_ws.update([pilots_df.columns.values.tolist()] + pilots_df.values.tolist())
                    st.success(f"{selected_name} assigned to {mission_id}.")

elif option == "View Drone Fleet":
    st.subheader("Drone Fleet Overview")
    st.dataframe(drones_df)
    st.subheader("Maintenance Alerts")
    maintenance = drones_df[drones_df["status"] == "Maintenance"]
    if maintenance.empty:
        st.success("No drones under maintenance.")
    else:
        st.warning("Drones Under Maintenance:")
        st.dataframe(maintenance)
