import pandas as pd
import sqlite3


def load_ssa():
    """Load SSA names data"""
    df = pd.read_csv("processed_ssa_names.csv").set_index("name")
    return df


def load_brothers():
    """Load brothers data"""
    df = pd.read_csv("brothers.csv").set_index("name")
    return df


def load_guests(on_campus_filepath, off_campus_filepath):
    """Load and process guest lists"""
    on_campus_df = pd.read_csv(on_campus_filepath, index_col=0)
    off_campus_df = pd.read_csv(off_campus_filepath, index_col=0)

    # Reshape data: Convert guest columns into rows
    on_melted = on_campus_df.stack().reset_index(level=1, drop=True).reset_index()
    on_melted.columns = ["brother", "name"]
    on_melted["campus_status"] = "On Campus"

    off_melted = off_campus_df.stack().reset_index(level=1, drop=True).reset_index()
    off_melted.columns = ["brother", "name"]
    off_melted["campus_status"] = "Off Campus"

    # Convert guest names to uppercase for consistency
    on_melted["name"] = on_melted["name"].str.upper()
    off_melted["name"] = off_melted["name"].str.upper()

    return on_melted, off_melted


def create_master():
    """Create master dataframe with guest info and store it in SQLite"""
    on_campus_df, off_campus_df = load_guests(
        "on_campus_guests.csv", "off_campus_guests.csv"
    )
    all_guests = pd.concat([on_campus_df, off_campus_df])

    brothers_data = load_brothers()

    # Merge guest data with brothers' class year
    master_df = pd.merge(
        all_guests, brothers_data, left_on="brother", right_index=True, how="left"
    )

    # Extract first name from full name
    master_df["first_name"] = master_df["name"].str.split().str[0]

    # Add gender data
    ssa_data = load_ssa()
    master_df = pd.merge(
        master_df, ssa_data, left_on="first_name", right_index=True, how="left"
    )

    # Drop first_name column if not needed
    master_df = master_df.drop(columns=["first_name"])

    # Initialize check-in columns
    master_df["check_in_time"] = pd.NaT
    master_df["check_in_status"] = "Not Checked In"

    # Convert NaT to None so SQLite can accept it
    master_df["check_in_time"] = master_df["check_in_time"].apply(
        lambda x: None if pd.isna(x) else x
    )

    # --- SAVE TO SQLITE ---
    conn = sqlite3.connect("party_monitor.db")
    cursor = conn.cursor()

    for _, row in master_df.iterrows():
        # Check if guest already exists (by name and brother)
        cursor.execute(
            """
            SELECT COUNT(*) FROM guests WHERE name = ? AND brother = ?
        """,
            (row["name"], row["brother"]),
        )

        exists = cursor.fetchone()[0]

        if not exists:  # If guest is not in DB, insert them
            cursor.execute(
                """
                INSERT INTO guests (name, brother, year, gender, campus_status, check_in_time, check_in_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    row["name"],
                    row["brother"],
                    row["year"],
                    row["gender"],
                    row["campus_status"],
                    row["check_in_time"],  # Now properly converted
                    row["check_in_status"],
                ),
            )

    # Commit and close the connection
    conn.commit()
    conn.close()

    return master_df
