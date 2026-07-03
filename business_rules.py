"""Business rule engine for ADO ticket hierarchy."""

from typing import Any, Dict, List, Optional

import streamlit as st

# --- Status constants ---
DONE_STATUSES = {"done", "dev done"}
ON_HOLD_STATUS = "on-hold"


# --- Status helpers ---
def is_done(status: str) -> bool:
    return (status or "").strip().lower() in DONE_STATUSES


def is_on_hold(status: str) -> bool:
    return (status or "").strip().lower() == ON_HOLD_STATUS


# --- Rule evaluation (pure logic) ---
def infer_story_status(subtasks: List[dict]) -> Optional[str]:
    if not subtasks:
        return None
    if all(is_done(s.get("Status", "")) for s in subtasks):
        return "dev done"
    return "in dev"


def evaluate_story(story_group: dict) -> dict:
    story = story_group["story"]
    subtasks = story_group["subtasks"]
    actual_status = story.get("Status", "")
    inferred = infer_story_status(subtasks)
    manual_reviews = []

    if inferred == "dev done" and not is_done(actual_status):
        manual_reviews.append({
            "ticket": story,
            "reason": "All subtasks completed but story status not updated.",
        })

    if inferred == "in dev" and is_done(actual_status):
        manual_reviews.append({
            "ticket": story,
            "reason": "Story marked complete but subtasks still pending.",
        })

    return {
        "story": story,
        "subtasks": subtasks,
        "inferred_status": inferred,
        "manual_reviews": manual_reviews,
    }


def collect_blocked_tickets(tickets: List[dict]) -> List[dict]:
    return [t for t in tickets if is_on_hold(t.get("Status", ""))]


def evaluate_feature_group(group: dict) -> dict:
    feature = group["feature"]
    story_evaluations = [evaluate_story(sg) for sg in group["stories"]]

    all_tickets = [feature]
    for se in story_evaluations:
        all_tickets.append(se["story"])
        all_tickets.extend(se["subtasks"])

    total_stories = len(story_evaluations)
    dev_done_stories = [
        se for se in story_evaluations if se["inferred_status"] == "dev done"
    ]
    in_progress_stories = [
        se for se in story_evaluations if se["inferred_status"] == "in dev"
    ]
    completion_pct = (
        (len(dev_done_stories) / total_stories * 100) if total_stories else 0.0
    )

    return {
        "feature": feature,
        "completion_pct": round(completion_pct, 1),
        "total_stories": total_stories,
        "dev_done_stories": dev_done_stories,
        "in_progress_stories": in_progress_stories,
        "blocked": collect_blocked_tickets(all_tickets),
        "manual_reviews": [
            item for se in story_evaluations for item in se["manual_reviews"]
        ],
    }


def evaluate_business_rules(grouped: List[dict], unlinked: List[dict]) -> dict:
    """Entry point: takes output of group_hierarchy(), returns report dict."""
    return {
        "feature_reports": [evaluate_feature_group(g) for g in grouped],
        "unlinked_blocked": collect_blocked_tickets(unlinked),
    }


# --- Streamlit UI ---
def render_business_report(report: dict) -> None:
    st.subheader("Business Rules Report")

    for fr in report["feature_reports"]:
        feature = fr["feature"]
        st.markdown(f"### Feature: {feature['Ticket ID']} {feature.get('Title', '')}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Completion %", f"{fr['completion_pct']}%")
        c2.metric("Dev Done Stories", len(fr["dev_done_stories"]))
        c3.metric("In Progress Stories", len(fr["in_progress_stories"]))
        c4.metric("Blocked", len(fr["blocked"]))

        if fr["dev_done_stories"]:
            with st.expander("Completed Stories (Dev Done)"):
                for se in fr["dev_done_stories"]:
                    s = se["story"]
                    st.markdown(
                        f"- {s['Ticket ID']} {s.get('Title', '')} "
                        f"[Actual: {s.get('Status', '')}]"
                    )

        if fr["in_progress_stories"]:
            with st.expander("In Progress Stories"):
                for se in fr["in_progress_stories"]:
                    s = se["story"]
                    pending = [
                        sub["Ticket ID"]
                        for sub in se["subtasks"]
                        if not is_done(sub.get("Status", ""))
                    ]
                    st.markdown(
                        f"- {s['Ticket ID']} {s.get('Title', '')} "
                        f"[Actual: {s.get('Status', '')}] "
                        f"(Pending subtasks: {', '.join(pending) or '—'})"
                    )

        if fr["blocked"]:
            with st.expander("Blocked Tickets (on-hold)"):
                for t in fr["blocked"]:
                    st.markdown(
                        f"- **{t.get('Type', '').title()}:** "
                        f"{t['Ticket ID']} {t.get('Title', '')} "
                        f"[Status: {t.get('Status', '')}]"
                    )

        if fr["manual_reviews"]:
            with st.expander("Manual Review Required", expanded=True):
                for item in fr["manual_reviews"]:
                    t = item["ticket"]
                    st.warning(
                        f"**{t['Ticket ID']}** {t.get('Title', '')} "
                        f"[Status: {t.get('Status', '')}] — {item['reason']}"
                    )

        st.markdown("---")

    if report["unlinked_blocked"]:
        st.subheader("Blocked Tickets (Unlinked)")
        for t in report["unlinked_blocked"]:
            st.markdown(
                f"- **{t.get('Type', '').title()}:** "
                f"{t['Ticket ID']} {t.get('Title', '')} "
                f"[Status: {t.get('Status', '')}]"
            )