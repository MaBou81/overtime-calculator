"""
Overtime / On-call Intervention Calculator
===========================================
Calculates overtime rates for interventions based on Belgian labor rules.

Rates:
- 130%: Weekday nights (20:00-06:00) - planned only
- 150%: Friday 20:00+ and Saturday until 20:00 - planned only
- 200%: Sundays, holidays, Saturday 20:00+, or urgent interventions outside business hours
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import holidays
import io
from typing import Tuple

# ======================================
# CONFIG
# ======================================
st.set_page_config(page_title="Overtime Calculator", layout="wide")
st.title("⏰ Overtime / On-call Intervention Calculator")

# Required columns in the Excel file
REQUIRED_COLUMNS = [
    "WOT",
    "WOT_Received_Date",
    "WOT_Received_Time",
    "Location",
    "Description",
    "Start_Date",
    "Start_Time",
    "End_Date",
    "End_Time",
    "Intervention_Type",
]

BE_HOLIDAYS = holidays.Belgium()

# ======================================
# HELPERS
# ======================================
def is_holiday(d: datetime.date) -> bool:
    """Check if a date is a Belgian public holiday."""
    return d in BE_HOLIDAYS


def minutes_to_hhmm(m: int) -> str:
    """Convert minutes to HH:MM format."""
    return f"{m//60:02d}:{m%60:02d}"


def hhmm_to_minutes(v: str) -> int:
    """Convert HH:MM format to minutes."""
    try:
        h, m = v.split(":")
        return int(h) * 60 + int(m)
    except:
        return 0


def normalize_type(v) -> str:
    """Normalize intervention type to 'urgent' or 'planned'."""
    if pd.isna(v):
        return ""
    v = str(v).strip().lower()
    if "urg" in v:
        return "urgent"
    if "plan" in v:
        return "planned"
    return ""


def get_rate_for_minute(dt: datetime, intervention_type: str) -> int:
    """
    Determine the overtime rate (0, 130, 150, or 200) for a specific minute.
    
    Args:
        dt: The datetime to evaluate
        intervention_type: 'urgent' or 'planned'
    
    Returns:
        0, 130, 150, or 200 representing the rate percentage
    """
    d = dt.date()
    tm = dt.time()
    weekday = d.weekday()  # 0=Monday, 6=Sunday
    is_hol = is_holiday(d)
    
    # ---------- URGENT ----------
    if intervention_type == "urgent":
        # Outside business hours (before 7:30 or after 18:00) OR weekends OR holidays
        if tm >= time(18, 0) or tm < time(7, 30) or weekday >= 5 or is_hol:
            return 200
        return 0
    
    # ---------- PLANNED ----------
    elif intervention_type == "planned":
        
        # --- 200% ---
        # Holidays, Sunday all day, Saturday from 20:00, Monday until 06:00
        if is_hol:
            return 200
        if weekday == 6:  # Sunday
            return 200
        if weekday == 5 and tm >= time(20, 0):  # Saturday from 20:00
            return 200
        if weekday == 0 and tm < time(6, 0):  # Monday until 06:00
            return 200
        
        # --- 150% ---
        # Friday from 20:00, Saturday until 20:00
        if weekday == 4 and tm >= time(20, 0):  # Friday from 20:00
            return 150
        if weekday == 5 and tm < time(20, 0):  # Saturday until 20:00
            return 150
        
        # --- 130% ---
        # Weekday nights (20:00-06:00)
        if tm >= time(20, 0) or tm < time(6, 0):
            return 130
        
        return 0
    
    return 0


def calculate_overtime_optimized(start_dt: datetime, end_dt: datetime, intervention_type: str) -> Tuple[int, int, int]:
    """
    Calculate overtime minutes for each rate category (optimized version).
    
    Instead of iterating minute by minute, we:
    1. Split the intervention into day segments
    2. For each segment, identify time blocks with the same rate
    3. Calculate minutes for each block
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        intervention_type: 'urgent' or 'planned'
    
    Returns:
        Tuple of (minutes_130, minutes_150, minutes_200)
    """
    if pd.isna(start_dt) or pd.isna(end_dt):
        return (0, 0, 0)
    
    if start_dt >= end_dt:
        return (0, 0, 0)
    
    m130 = m150 = m200 = 0
    
    # Define time boundaries that matter for rate changes
    time_boundaries = [
        time(0, 0),   # Midnight
        time(6, 0),   # End of night shift
        time(7, 30),  # Start of business hours (urgent)
        time(18, 0),  # End of business hours (urgent)
        time(20, 0),  # Start of evening rates
        time(23, 59), # End of day
    ]
    
    current = start_dt
    
    # Process day by day to handle date changes properly
    while current < end_dt:
        day_start = current
        day_end = min(
            datetime.combine(current.date(), time(23, 59)) + timedelta(minutes=1),
            end_dt
        )
        
        # For each day, process time blocks
        last_boundary = day_start.time()
        last_rate = get_rate_for_minute(day_start, intervention_type)
        
        for boundary in time_boundaries:
            if boundary <= last_boundary:
                continue
            
            block_start = datetime.combine(current.date(), last_boundary)
            block_end = datetime.combine(current.date(), boundary)
            
            # Only process blocks within our intervention window
            block_start = max(block_start, day_start)
            block_end = min(block_end, day_end)
            
            if block_start >= block_end:
                continue
            
            # Calculate minutes in this block
            minutes = int((block_end - block_start).total_seconds() / 60)
            
            if minutes > 0:
                # Use the rate at the start of the block
                rate = get_rate_for_minute(block_start, intervention_type)
                
                if rate == 130:
                    m130 += minutes
                elif rate == 150:
                    m150 += minutes
                elif rate == 200:
                    m200 += minutes
            
            last_boundary = boundary
        
        # Handle the last segment of the day
        if day_end > datetime.combine(current.date(), last_boundary):
            block_start = max(datetime.combine(current.date(), last_boundary), day_start)
            minutes = int((day_end - block_start).total_seconds() / 60)
            
            if minutes > 0:
                rate = get_rate_for_minute(block_start, intervention_type)
                if rate == 130:
                    m130 += minutes
                elif rate == 150:
                    m150 += minutes
                elif rate == 200:
                    m200 += minutes
        
        # Move to next day
        current = datetime.combine(current.date() + timedelta(days=1), time(0, 0))
    
    return (m130, m150, m200)


def calculate_overtime(row: pd.Series) -> pd.Series:
    """
    Calculate overtime for a single intervention row.
    
    Args:
        row: DataFrame row with _start_dt, _end_dt, and _type
    
    Returns:
        Series with 130%, 150%, and 200% columns in HH:MM format
    """
    start = row["_start_dt"]
    end = row["_end_dt"]
    intervention_type = row["_type"]
    
    m130, m150, m200 = calculate_overtime_optimized(start, end, intervention_type)
    
    return pd.Series({
        "130%": minutes_to_hhmm(m130),
        "150%": minutes_to_hhmm(m150),
        "200%": minutes_to_hhmm(m200),
    })


# ======================================
# MAIN
# ======================================

# Instructions
with st.expander("ℹ️ Instructions & Rate Explanation"):
    st.markdown("""
    ### How to use
    1. Upload an Excel file with intervention data
    2. The file must contain these columns: WOT, WOT_Received_Date, WOT_Received_Time, Location, Description, Start_Date, Start_Time, End_Date, End_Time, Intervention_Type
    3. Review the calculated overtime rates
    4. Download the results
    
    ### Overtime Rates
    - **130%**: Weekday nights (20:00-06:00) - planned interventions only
    - **150%**: Friday 20:00+ and Saturday until 20:00 - planned interventions only
    - **200%**: Sundays, holidays, Saturday 20:00+, Monday until 06:00, or urgent interventions outside business hours (before 7:30 or after 18:00)
    
    ### Intervention Types
    - **Urgent**: Any intervention containing "urg" in the type
    - **Planned**: Any intervention containing "plan" in the type
    """)

uploaded_file = st.file_uploader("📁 Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        
        # Validate required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            st.info("Your file must contain these columns: " + ", ".join(REQUIRED_COLUMNS))
            st.stop()
        
        st.success(f"✅ File loaded successfully: {len(df)} rows")
        
        # --- KEEP BUSINESS DATES CLEAN (NO TIME) ---
        df["WOT_Received_Date"] = df["WOT_Received_Date"].astype(str)
        df["Start_Date"] = df["Start_Date"].astype(str)
        df["End_Date"] = df["End_Date"].astype(str)
        
        # --- INTERNAL datetime ONLY for calculation ---
        df["_start_dt"] = pd.to_datetime(
            df["Start_Date"] + " " + df["Start_Time"].astype(str),
            errors="coerce"
        )
        
        df["_end_dt"] = pd.to_datetime(
            df["End_Date"] + " " + df["End_Time"].astype(str),
            errors="coerce"
        )
        
        # Check for invalid dates
        invalid_dates = df[df["_start_dt"].isna() | df["_end_dt"].isna()]
        if len(invalid_dates) > 0:
            st.warning(f"⚠️ {len(invalid_dates)} rows have invalid dates/times and will be skipped")
            with st.expander("Show invalid rows"):
                st.dataframe(invalid_dates[REQUIRED_COLUMNS])
        
        # Check for reversed dates (end before start)
        reversed_dates = df[df["_start_dt"] >= df["_end_dt"]]
        if len(reversed_dates) > 0:
            st.warning(f"⚠️ {len(reversed_dates)} rows have end time before start time (will return 0 overtime)")
            with st.expander("Show reversed date rows"):
                st.dataframe(reversed_dates[["WOT", "Start_Date", "Start_Time", "End_Date", "End_Time"]])
        
        df["_type"] = df["Intervention_Type"].apply(normalize_type)
        
        # Check for unrecognized intervention types
        unknown_types = df[~df["_type"].isin(["urgent", "planned"]) & df["_type"].notna() & (df["_type"] != "")]
        if len(unknown_types) > 0:
            st.warning(f"⚠️ {len(unknown_types)} rows have unrecognized intervention types (will return 0 overtime)")
            with st.expander("Show unrecognized types"):
                st.dataframe(unknown_types[["WOT", "Intervention_Type"]])
        
        # Calculate overtime with progress bar
        with st.spinner("Calculating overtime..."):
            results = df.apply(calculate_overtime, axis=1)
        
        # ======================================
        # OPTIONAL INDICATIVE SURCHARGE
        # ======================================
        st.sidebar.subheader("💰 Indicative surcharge")
        st.sidebar.caption("Information only - not for official use")
        
        hourly_rate = st.sidebar.number_input(
            "Hourly salary (€)",
            min_value=0.0,
            value=50.0,
            step=1.0,
            help="Your base hourly rate for calculation purposes"
        )
        
        fixed_bonus = st.sidebar.number_input(
            "Fixed bonus per period (€)",
            min_value=0.0,
            value=140.0,
            step=10.0,
            help="Fixed amount added to the total"
        )
        
        # Calculate total surcharge
        total_minutes_130 = results["130%"].apply(hhmm_to_minutes).sum()
        total_minutes_150 = results["150%"].apply(hhmm_to_minutes).sum()
        total_minutes_200 = results["200%"].apply(hhmm_to_minutes).sum()
        
        surcharge_130 = (total_minutes_130 / 60) * hourly_rate * 0.30
        surcharge_150 = (total_minutes_150 / 60) * hourly_rate * 0.50
        surcharge_200 = (total_minutes_200 / 60) * hourly_rate * 1.00
        
        surcharge_total = surcharge_130 + surcharge_150 + surcharge_200 + fixed_bonus
        
        st.sidebar.metric(
            "Total 130% hours",
            minutes_to_hhmm(total_minutes_130),
            delta=f"€{surcharge_130:.2f}"
        )
        st.sidebar.metric(
            "Total 150% hours",
            minutes_to_hhmm(total_minutes_150),
            delta=f"€{surcharge_150:.2f}"
        )
        st.sidebar.metric(
            "Total 200% hours",
            minutes_to_hhmm(total_minutes_200),
            delta=f"€{surcharge_200:.2f}"
        )
        st.sidebar.divider()
        st.sidebar.metric(
            "Fixed bonus",
            f"€{fixed_bonus:.2f}"
        )
        st.sidebar.metric(
            "🎯 Total surcharge",
            f"€{surcharge_total:.2f}",
            help="Sum of all overtime surcharges plus fixed bonus"
        )
        
        # ======================================
        # FINAL EXPORT (BUSINESS ONLY)
        # ======================================
        final_df = pd.concat(
            [
                df[REQUIRED_COLUMNS],
                results
            ],
            axis=1
        )
        
        st.subheader("📊 Calculated overtime")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total interventions", len(df))
        with col2:
            urgent_count = len(df[df["_type"] == "urgent"])
            st.metric("Urgent", urgent_count)
        with col3:
            planned_count = len(df[df["_type"] == "planned"])
            st.metric("Planned", planned_count)
        
        # Display results
        st.dataframe(final_df, use_container_width=True)
        
        # Export to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            final_df.to_excel(writer, sheet_name="Overtime Results", index=False)
            
            # Add summary sheet
            summary_df = pd.DataFrame({
                "Category": ["130% hours", "150% hours", "200% hours", "Fixed bonus", "Total surcharge"],
                "Value": [
                    minutes_to_hhmm(total_minutes_130),
                    minutes_to_hhmm(total_minutes_150),
                    minutes_to_hhmm(total_minutes_200),
                    f"€{fixed_bonus:.2f}",
                    f"€{surcharge_total:.2f}"
                ],
                "Amount (€)": [
                    f"{surcharge_130:.2f}",
                    f"{surcharge_150:.2f}",
                    f"{surcharge_200:.2f}",
                    f"{fixed_bonus:.2f}",
                    f"{surcharge_total:.2f}"
                ]
            })
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        output.seek(0)
        
        st.download_button(
            "📥 Download result Excel",
            data=output,
            file_name=f"overtime_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please make sure your Excel file is properly formatted and contains all required columns.")
        
else:
    # Show example format when no file is uploaded
    st.info("👆 Upload an Excel file to get started")
    
    with st.expander("📋 Example file format"):
        example_df = pd.DataFrame({
            "WOT": ["WOT001", "WOT002"],
            "WOT_Received_Date": ["2024-01-15", "2024-01-16"],
            "WOT_Received_Time": ["08:30", "14:00"],
            "Location": ["Building A", "Building B"],
            "Description": ["Server issue", "Network problem"],
            "Start_Date": ["2024-01-15", "2024-01-16"],
            "Start_Time": ["21:00", "19:00"],
            "End_Date": ["2024-01-15", "2024-01-17"],
            "End_Time": ["23:30", "02:00"],
            "Intervention_Type": ["urgent", "planned"]
        })
        st.dataframe(example_df)
        
        # Provide example download
        example_output = io.BytesIO()
        example_df.to_excel(example_output, index=False, engine="openpyxl")
        example_output.seek(0)
        
        st.download_button(
            "📥 Download example template",
            data=example_output,
            file_name="overtime_calculator_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
