import pandas as pd
import streamlit as st
from typing import Optional
from business_rules import evaluate_business_rules, render_business_report
from gemini_client import generate_ai_summary

REQUIRED_COLUMNS = ["Ticket ID", "Type", "Parent", "Status", "Title", "Description"]
VALID_TYPES = {"feature", "story", "subtask"}

def normalize_id(value):
    """Normalize ticket/parent IDs: blank → NA, strip Excel float artifacts."""
    if pd.isna(value):
        return pd.NA
    s = str(value).strip()
    if s.lower() in ("", "nan", "none", "<na>"):
        return pd.NA
    # Excel float column: 23443.0 → "23443"
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize text fields per requirements."""
    df = df.copy()

    for col in ["Ticket ID", "Type", "Parent", "Status", "Title", "Description"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": "", "None": ""})

    df["Type"] = df["Type"].str.lower()
    df["Status"] = df["Status"].str.lower()

    df["Ticket ID"] = df["Ticket ID"].apply(normalize_id)
    df["Parent"] = df["Parent"].apply(normalize_id)
    # Drop rows with no Ticket ID
    df["Ticket ID"] = df["Ticket ID"].astype("string")
    df["Parent"] = df["Parent"].astype("string")  # keeps <NA> for blank Parent

    return df


def build_lookup(df: pd.DataFrame) -> dict:
    """Map Ticket ID -> row dict."""
    lookup = {}
    for _, row in df.iterrows():
        ticket_id = row["Ticket ID"]
        if ticket_id:
            lookup[ticket_id] = row.to_dict()
    return lookup


def is_valid_hierarchy(feature_id: str, story_id: str, subtask_row: dict, lookup: dict) -> bool:
    """Check Feature → Story → Subtask chain."""
    story = lookup.get(story_id)
    if story is None or story.get("Type") != "story":
        return False
    story_parent = story.get("Parent")
    subtask_parent = subtask_row.get("Parent")
    if pd.isna(story_parent) or pd.isna(subtask_parent):
        return False
    if str(story_parent) != str(feature_id):
        return False
    if subtask_row.get("Type") != "subtask":
        return False
    return str(subtask_parent) == str(story_id)


def group_hierarchy(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """
    Returns:
      - grouped: list of Feature groups with nested Stories and Subtasks
      - unlinked: tickets that couldn't be placed in a valid hierarchy
    """
    lookup = build_lookup(df)
    used_ids: set[str] = set()
    grouped: list[dict] = []

    features = df[df["Type"] == "feature"].copy()

    for _, feature in features.iterrows():
        feature_id = feature["Ticket ID"]
        feature_group = {
            "feature": feature.to_dict(),
            "stories": [],
        }

        # Stories whose parent is this Feature
        stories = df[
               (df["Type"] == "story")
                & df["Parent"].notna()
                & (df["Parent"] == feature_id)
        ]
    
        for _, story in stories.iterrows():
            story_id = story["Ticket ID"]
            story_group = {
                "story": story.to_dict(),
                "subtasks": [],
            }

            subtasks = df[
                (df["Type"] == "subtask")
                & df["Parent"].notna()
                & (df["Parent"] == story_id)
            ]

            for _, subtask in subtasks.iterrows():
                if is_valid_hierarchy(feature_id, story_id, subtask.to_dict(), lookup):
                    story_group["subtasks"].append(subtask.to_dict())
                    used_ids.add(subtask["Ticket ID"])

            feature_group["stories"].append(story_group)
            used_ids.add(story_id)

        grouped.append(feature_group)
        used_ids.add(feature_id)

    # Anything not placed goes to Unlinked Tickets
    unlinked = []
    for _, row in df.iterrows():
        ticket_id = row["Ticket ID"]
        if ticket_id not in used_ids:
            unlinked.append(row.to_dict())

    return grouped, unlinked


def format_ticket_line(ticket: dict, indent: str = "", label: str = "") -> str:
    ticket_id = ticket.get("Ticket ID", "")
    title = ticket.get("Title", "")
    status = ticket.get("Status", "")
    prefix = f"{indent}{label}: {ticket_id} {title}"
    if status:
        prefix += f" [Status: {status}]"
    return prefix


def render_hierarchy(grouped: list[dict], unlinked: list[dict]) -> None:
    if not grouped and not unlinked:
        st.info("No tickets found.")
        return

    for group in grouped:
        feature = group["feature"]
        st.markdown(f"**Feature:** {feature['Ticket ID']} {feature.get('Title', '')}")

        for story_group in group["stories"]:
            story = story_group["story"]
            status = story.get("Status", "")
            status_text = f" [Status: {status}]" if status else ""
            st.markdown(
                f"&nbsp;&nbsp;**Story:** {story['Ticket ID']} {story.get('Title', '')}{status_text}"
            )

            for subtask in story_group["subtasks"]:
                sub_status = subtask.get("Status", "")
                sub_status_text = f" [Status: {sub_status}]" if sub_status else ""
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Subtask:** "
                    f"{subtask['Ticket ID']} {subtask.get('Title', '')}{sub_status_text}"
                )

        st.markdown("")  # spacing between feature groups

    if unlinked:
        st.markdown("---")
        st.subheader("Unlinked Tickets")
        for ticket in unlinked:
            ttype = ticket.get("Type", "")
            ticket_id = ticket.get("Ticket ID", "")
            title = ticket.get("Title", "")
            status = ticket.get("Status", "")
            parent = ticket.get("Parent", "")
            status_text = f" [Status: {status}]" if status else ""
            parent_text = f" (Parent: {parent})" if parent else ""
            st.markdown(
                f"- **{ttype.title()}:** {ticket_id} {title}{status_text}{parent_text}"
            )


def main() -> None:
    st.set_page_config(page_title="ADO Ticket Hierarchy", layout="wide")
    st.title("ADO Ticket Hierarchy Viewer")
    st.caption("Upload an Excel export to view Feature → Story → Subtask hierarchy.")

    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

    if uploaded_file is None:
        st.info("Upload an `.xlsx` file with columns: Ticket ID, Type, Parent, Status, Title, Description.")
        return

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as exc:
        st.error(f"Failed to read Excel file: {exc}")
        return

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.write("Found columns:", list(df.columns))
        return

    df = normalize_dataframe(df)
    df = df[df["Ticket ID"] != ""]  # drop empty rows

    grouped, unlinked = group_hierarchy(df)

     # --- NEW: business rules (uses grouped + unlinked from above) ---
    print("Evaluating business rules...")
    feature_report = evaluate_business_rules(grouped, unlinked)
    render_business_report(feature_report)
    # --- END NEW ---

    # Calling AI for summmary
    print("calling AI for summary...")
    with st.spinner("Generating AI delivery insights..."):
        # success, ai_summary = generate_ai_summary(feature_report)
        result = generate_ai_summary(feature_report)

        st.write(type(result))
        st.write(result)

        st.stop()
    # Displaying the summary
    st.header("## 🤖 AI Project Summary")
    #st.markdown(ai_summary)
    if success:
        st.write("Executive Summary:", ai_summary["executive_summary"])
        st.subheader("⚠ Delivery Risks")

        for risk in ai_summary["delivery_risks"]:
            st.write(f"• {risk}")

        st.subheader("✅ Suggested PM Actions")

        for action in ai_summary["pm_actions"]:
            st.write(f"• {action}")

        quality = ai_summary["analysis_quality"]

        st.subheader("📊 Analysis Quality")

        st.metric(
            "Confidence",
            quality["confidence"]
        )

        st.caption(quality["reason"])
    else:
        st.error(f"Failed to generate AI summary. Error: {result['error']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Features", len(df[df["Type"] == "feature"]))
    col2.metric("Stories", len(df[df["Type"] == "story"]))
    col3.metric("Unlinked", len(unlinked))

    with st.expander("Raw normalized data"):
        st.dataframe(df, use_container_width=True)

    st.subheader("Ticket Hierarchy")
    render_hierarchy(grouped, unlinked)


if __name__ == "__main__":
    main()