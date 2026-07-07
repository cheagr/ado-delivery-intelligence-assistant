import pandas as pd

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


def parse_excel(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as exc:
        # st.error(f"Failed to read Excel file: {exc}")
        return False, {
        "error": f"Failed to read Excel file: {exc}"
        }

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        # st.error(f"Missing required columns: {', '.join(missing)}")
        # st.write("Found columns:", list(df.columns))
        return False, {
            "error": (
                f"Missing required columns: {', '.join(missing)}\n"
                f"Found columns: {list(df.columns)}"
            )
        }

    df = normalize_dataframe(df)
    df = df[df["Ticket ID"] != ""]  # drop empty rows

    grouped, unlinked = group_hierarchy(df)

    return True, {
    "dataframe": df,
    "grouped": grouped,
    "unlinked": unlinked
    }  