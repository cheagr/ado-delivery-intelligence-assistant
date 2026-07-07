AI_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {
            "type": "string"
        },
        "delivery_risks": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "pm_actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "manual_review_items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "analysis_quality": {
            "type": "object",
            "properties": {
                "confidence": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            }
        }
    }
}