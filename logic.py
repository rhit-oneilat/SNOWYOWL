from datetime import datetime
import sqlite3

import pandas as pd
from guest_list import create_master


class PartyMonitor:
    def __init__(self):
        self.master_df = None

    def process_guest_list(self, on_campus_df, off_campus_df):
        """Process and combine guest lists with master data"""
        self.master_df = create_master()
        return self.master_df

    def check_in_guest(self, guest_name):
        conn = sqlite3.connect("party_monitor.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE guests
            SET check_in_time = ?, check_in_status = ?
            WHERE name = ?
        """,
            (datetime.now(), "Checked In", guest_name),
        )
        conn.commit()
        conn.close()

    def load_guests(self):
        conn = sqlite3.connect("party_monitor.db")
        query = "SELECT * FROM guests"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def get_real_time_stats(self, df):
        """Calculate real-time party statistics"""
        total_guests = len(df)
        checked_in = df["check_in_status"].value_counts().get("Checked In", 0)

        # Ensure missing categories default to 0
        gender_ratio = df["gender"].value_counts(normalize=True).to_dict()
        campus_ratio = df["campus_status"].value_counts(normalize=True).to_dict()

        return {
            "Total Guests": total_guests,
            "Checked In": checked_in,
            "Remaining": total_guests - checked_in,
            "Percent of Guests that are women": f"{gender_ratio.get('F', 0) * 100:.0f}%",
            "Percent of Guests from Rose ": f"{campus_ratio.get('On Campus', 0) * 100:.0f}%",
        }

    def filter_guest_list(self, df, status_filter, location_filter, class_filter):
        """Apply filters to guest list"""
        filtered_df = df.copy()
        filtered_df["year"] = filtered_df["year"].astype(str)

        if class_filter != "All":
            filtered_df = filtered_df[filtered_df["year"] == class_filter]

        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["check_in_status"] == status_filter]

        if location_filter != "All":
            filtered_df = filtered_df[filtered_df["campus_status"] == location_filter]

        # Ensure 'name' is included in the returned DataFrame
        return filtered_df[
            [
                "name",  # <-- Added this back to the returned DataFrame
                "brother",
                "year",
                "gender",
                "campus_status",
                "check_in_time",
                "check_in_status",
            ]
        ]

    def get_brother_guest_counts(self):
        """Get guest count per brother"""
        return self.master_df.groupby("brother").size().sort_values(ascending=False)

    def get_gender_distribution(self):
        """Get gender distribution of guests"""
        return self.master_df["gender"].value_counts()

    def check_out_guest(self, guest_name):
        conn = sqlite3.connect("party_monitor.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE guests
            SET check_in_time = NULL, check_in_status = ?
            WHERE name = ?
        """,
            ("Not Checked In", guest_name),
        )
        conn.commit()
        conn.close()
