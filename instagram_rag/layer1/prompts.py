# ============================================================
#  IDENTITY PROMPT — edit this section yourself
#  This is the only file you need to modify to change
#  how the model reasons about Instagram data.
# ============================================================

# System instructions
system_prompt = """
[PLACE YOUR IDENTITY AND SYSTEM INSTRUCTIONS HERE]

Example structure:
You are a social media analytics AI for [brand name].
Your tone is [tone]. Your focus is [focus area].

The input will be a JSON object of Instagram post metrics.
"""

# ============================================================
#  OUTPUT SCHEMA — do not edit below this line
#  The model is instructed to always return this exact JSON shape.
# ============================================================

output_schema = """
Output MUST be a valid JSON object with these exact keys:
{
  "post_id":            string   — the post identifier,
  "overall_sentiment":  string   — positive | negative | neutral | mixed,
  "sentiment_score":    float    — -1.0 to 1.0,
  "dominant_emotion":   string   — excitement | anger | disappointment | joy | sarcasm | neutral,
  "aspect_breakdown": {
    "content_quality":  float or null,
    "posting_timing":   float or null,
    "audience_reach":   float or null,
    "engagement_depth": float or null
  },
  "top_themes":         list[string] — up to 3 themes,
  "narrative_shift":    string   — improving | declining | stable | volatile,
  "strategic_signals": {
    "risk_level":       string   — low | medium | high,
    "opportunity":      string or null,
    "urgency":          string   — low | medium | high,
    "viral_risk":       boolean
  },
  "best_action":        string   — one concrete next step,
  "confidence":         float    — 0.0 to 1.0
}
Only return JSON. No prose. No markdown.
"""

# Combined prompt — used by processor.py — do not edit
FULL_SYSTEM_PROMPT = system_prompt.strip() + "\n\n" + output_schema.strip()
