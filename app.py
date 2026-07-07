import pandas as pd
import streamlit as st
from typing import Optional
from business_rules import evaluate_business_rules, render_business_report
from gemini_client import generate_ai_summary
from excel_parser import parse_excel


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

    success, parsed = parse_excel(uploaded_file)

    if not success:
        st.error(parsed["error"])
        return

    df = parsed["dataframe"]
    grouped = parsed["grouped"]
    unlinked = parsed["unlinked"]

     # --- NEW: business rules (uses grouped + unlinked from above) ---
    print("Evaluating business rules...")
    feature_report = evaluate_business_rules(grouped, unlinked)
    render_business_report(feature_report)
    # --- END NEW ---

    # Calling AI for summmary
    print("calling AI for summary...")
    with st.spinner("Generating AI delivery insights..."):
        success, ai_summary = generate_ai_summary(feature_report)
        # result = generate_ai_summary(feature_report)

        # st.write(type(result))
        # st.write(result)

        # st.stop()
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
        st.error(f"Failed to generate AI summary. Error: {ai_summary['error']}")

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