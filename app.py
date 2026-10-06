"""PlainSpeak — paste the confusing, get the clear.

Run:  python app.py        ->  http://127.0.0.1:5000
Live AI: set LLM_API_KEY (any OpenAI-compatible key). Without it, the app
runs in clearly-labelled demo mode.
"""
import os

from flask import Flask, jsonify, render_template, request

import fallback
import llm
import readability

app = Flask(__name__)

LEVELS = ("age12", "plain", "pro")
MIN_CHARS = 50
MAX_CHARS = 5000

SAMPLES = {
    "medical": (
        "Medical discharge note",
        "The patient, a 58-year-old male with a history of hypertension and "
        "hyperlipidemia, presented with acute chest discomfort. Subsequent "
        "diagnostic evaluation demonstrated elevated troponin levels consistent "
        "with a non-ST-elevation myocardial infarction. The cardiology team "
        "administered dual antiplatelet therapy and prescribed a high-intensity "
        "statin prior to discharge. The patient was advised to obtain follow-up "
        "evaluation within seven days, and to terminate tobacco utilization "
        "immediately due to the fact that continued smoking substantially "
        "increases the probability of subsequent cardiac events.",
    ),
    "legal": (
        "Freelance contract clause",
        "Notwithstanding anything to the contrary herein, the Contractor hereby "
        "assigns to the Client all right, title, and interest in and to any and "
        "all work product, including but not limited to deliverables, "
        "documentation, and derivative works thereof, in perpetuity and "
        "throughout the universe. In the event that any such assignment is "
        "deemed ineffective for any reason, the Contractor agrees to execute "
        "any and all documents necessary to facilitate said assignment. "
        "Compensation pursuant to this agreement shall be remitted net thirty "
        "(30) days subsequent to receipt of a valid invoice.",
    ),
    "academic": (
        "Research abstract",
        "This study leverages a mixed-methodology paradigm to investigate the "
        "efficacy of spaced-repetition interventions on long-term retention in "
        "second-language vocabulary acquisition. Approximately 240 participants "
        "were administered a battery of assessments prior to and subsequent to "
        "a twelve-week intervention period. Results demonstrate a statistically "
        "significant improvement in retention metrics, notwithstanding "
        "considerable individual variation. One caveat: the methodology "
        "utilized has the ability to confound spacing effects with mere "
        "exposure time, a limitation future research should endeavor to expedite.",
    ),
}


@app.get("/")
def index():
    return render_template(
        "index.html",
        samples={k: v[0] for k, v in SAMPLES.items()},
        levels=LEVELS,
    )


@app.get("/api/samples/<name>")
def get_sample(name):
    if name not in SAMPLES:
        return jsonify({"error": "unknown sample"}), 404
    title, text = SAMPLES[name]
    return jsonify({"title": title, "text": text})


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "mode": "live" if llm.has_key() else "demo"})


@app.post("/api/simplify")
def simplify():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    level = data.get("level") or "plain"

    if not text:
        return jsonify({"error": "Paste some text first — anything confusing works."}), 400
    if len(text) < MIN_CHARS:
        return (
            jsonify(
                {
                    "error": f"That's only {len(text)} characters — paste at least "
                    f"{MIN_CHARS} so there's something to simplify."
                }
            ),
            400,
        )
    if len(text) > MAX_CHARS:
        return (
            jsonify(
                {"error": f"Keep it under {MAX_CHARS} characters (yours: {len(text)})."}
            ),
            400,
        )
    if level not in LEVELS:
        return jsonify({"error": "Unknown audience level."}), 400

    before = readability.analyze(text)

    if llm.has_key():
        try:
            result = llm.simplify(text, level)
        except llm.LLMError as exc:
            return (
                jsonify(
                    {
                        "error": "The AI didn't respond. Check your key and try again — "
                        "or run without a key for demo mode.",
                        "detail": str(exc),
                    }
                ),
                502,
            )
    else:
        result = fallback.simplify(text, level)

    after = readability.analyze(result["simplified"])
    result["readability_before"] = before
    result["readability_after"] = after
    result["readability_before"]["label"] = readability.grade_label(before["fk_grade"])
    result["readability_after"]["label"] = readability.grade_label(after["fk_grade"])
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)
