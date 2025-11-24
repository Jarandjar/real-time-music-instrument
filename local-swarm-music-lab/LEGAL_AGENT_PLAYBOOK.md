# Legal Agent Playbook

Companion reference for `REAL_TIME_AI_MUSIC_INSTRUMENT.md` and `SPARK_MISSION_LIST.md`. This playbook outlines Spark-ready missions, safe prompt rewriting logic, developer checklists, and an in-pipeline legal engine pattern to keep the real-time music instrument compliant while preserving creative flow.

---

## Mission Deck – Legal Agent Enablement

### Mission L1 – Policy & Schema Guardrails
- [ ] Define `LegalReviewConfig` schema describing allowed feature types, banned phrases, and escalation policy.
- [ ] Embed `legalNotes` and `sourceProvenance` fields inside every `StyleProfile` preset.
- [ ] Unit test that presets fail validation if they reference specific copyrighted song titles in musical directions.

*Acceptance:* JSON schema + pytest verifying disallowed tokens are rejected; presets include provenance text.

### Mission L2 – Prompt Sentinel Service
- [ ] Create `legal_prompt_rewriter.py` with rewrite rules (see section below) and deterministic test fixtures.
- [ ] Integrate middleware into backend so `/session`, `/generate-bar`, and model adapters funnel prompts through the rewriter.
- [ ] Log original + rewritten prompts (hashed) with reason codes for future audits.

*Acceptance:* Tests prove unsafe phrases become safe paraphrases; middleware blocks unhandled high-risk prompts with actionable error messages.

### Mission L3 – Style Analysis Compliance
- [ ] Wrap `/analyze-style` pipeline with a `LegalInspector` that enforces "high-level features only" output.
- [ ] Ensure temporary audio files are deleted immediately; record deletion confirmation in event spine.
- [ ] Provide redaction report summarizing what was removed or generalized.

*Acceptance:* Integration test shows uploaded WAV yields sanitized JSON; storage audit confirms no audio remnants; redaction report archived per session.

### Mission L4 – Output Similarity Monitoring
- [ ] Implement lightweight melodic similarity check (n-gram / interval fingerprints) for generated lead lines vs. banned motifs.
- [ ] Expose `/legal/review` endpoint to inspect last N bars, flagged reasons, and mitigation steps.
- [ ] Auto-trigger re-generation or variation when similarity exceeds threshold.

*Acceptance:* Synthetic test where generator intentionally mimics a motif triggers alert and replacement; `/legal/review` returns trace log.

### Mission L5 – Transparency & Developer Tooling
- [ ] Add "Legal Mode" panel in frontend showing current policy status, last rewrites, and analysis compliance.
- [ ] Provide CLI `legal_audit.py --session <id>` summarizing prompts, feature extractions, and similarity checks.
- [ ] Document SOP for updating policies (who approves, how to version).

*Acceptance:* Manual demo displays panel data; CLI outputs human-readable report; SOP stored in repo with checklist.

---

## Prompt Rewriting System

### Unsafe → Safe Translation Rules
1. **Exact song/artist replication requests**  
   - Pattern: `"sound exactly like <song>"`, `"recreate <artist> solo"`.  
   - Rewrite: replace with genre/era descriptors + technique (e.g., "southern-rock pentatonic climax").
2. **Direct melody/lyric copying**  
   - Pattern: mentions of "copy", "same notes", quoting lyrics.  
   - Action: reject if lyrics quoted; otherwise, rewrite to structural description ("call-and-response vocal phrasing").
3. **Disallowed proper nouns**  
   - Maintain blocklist of copyrighted titles/performers; swap to adjectives ("stadium rock anthem energy").
4. **Explicit instructions to extract raw audio/MIDI**  
   - Rewrite to "extract tempo, chord histogram, energy profile" and warn user about limitations.
5. **Ambiguous references**  
   - If user says "do that Queen opera thing", rewrite to "multi-voice stacked harmony with dramatic dynamics".

### Implementation Outline (`legal_prompt_rewriter.py`)
```python
from dataclasses import dataclass
from typing import List
import re

@dataclass
class RewriteResult:
    sanitized_prompt: str
    reasons: List[str]
    blocked: bool = False

BLOCKED_PHRASES = {"copy this melody", "replicate lyric"}
PROPER_NOUN_MAP = {
    "Free Bird": "southern-rock epic finale",
    "Bohemian Rhapsody": "layered operatic rock section",
    "Eruption": "high-gain tapping guitar solo"
}

def rewrite_prompt(user_prompt: str) -> RewriteResult:
    lower = user_prompt.lower()
    reasons: List[str] = []

    if any(p in lower for p in BLOCKED_PHRASES):
        return RewriteResult(sanitized_prompt="", reasons=["blocked: explicit copy request"], blocked=True)

    sanitized = user_prompt
    for proper, replacement in PROPER_NOUN_MAP.items():
        if proper.lower() in lower:
            sanitized = re.sub(proper, replacement, sanitized, flags=re.IGNORECASE)
            reasons.append(f"replaced {proper} → {replacement}")

    sanitized = re.sub(r"sound[s]? exactly like", "capture the vibe of", sanitized, flags=re.IGNORECASE)
    if sanitized != user_prompt:
        reasons.append("softened exact-match language")

    return RewriteResult(sanitized_prompt=sanitized.strip(), reasons=reasons)
```
*Tests:* feed known risky prompts, assert correct rewrite/blocks; ensure safe prompts pass unchanged.

---

## Copyright Safety Checklist

Use this checklist whenever you:
- add/edit presets,
- extend `/analyze-style`,
- update prompt templates,
- change rendering logic.

| # | Check | Pass? | Notes |
|---|---|---|---|
| 1 | Preset `meta.notes` only references eras/genres, not copyrighted riffs. | ☐ | |
| 2 | StyleProfile values derived from references are statistical (BPM, chord counts). | ☐ | |
| 3 | `/analyze-style` deletes raw audio immediately (log entry). | ☐ | |
| 4 | No presets or prompts contain direct lyric text. | ☐ | |
| 5 | Prompt templates routed through `rewrite_prompt` helper. | ☐ | |
| 6 | Similarity monitor thresholds configured + tested with known riffs. | ☐ | |
| 7 | Logs capture sanitized prompts & reason codes (hashed user content). | ☐ | |
| 8 | Frontend messaging clarifies "style, not replication" policy. | ☐ | |
| 9 | Legal audit CLI passes for latest session before release. | ☐ | |
|10 | Versioned policy doc updated & linked in README/legal section. | ☐ | |

Keep completed checklists in `compliance/logs/<date>-<release>.md`.

---

## In-Pipeline Legal Engine Sketch

```
[User Input]
   │
   ▼
Prompt Intake Layer
   │  (Legal Prompt Rewriter)
   ▼
Session Planner ──> StyleProfile Store
   │                ▲
   │                │ (Legal Inspector ensures presets safe)
   ▼
Generation Loop (per bar)
   │  ├─ Drum/Bass/Rhythm/Lead Generators
   │  └─ Similarity Monitor (interval fingerprints)
   ▼
Render & Stream
   │
   ▼
Logging & Audit Sink
```

### Module Responsibilities
- **LegalPromptMiddleware**: wraps FastAPI endpoints `/session`, `/session/{id}/style`, `/generate-bar`; calls `rewrite_prompt`, attaches `legal.reasons` metadata per request.
- **LegalInspector**: invoked by `/analyze-style`; validates outgoing JSON, strips raw features, records `analysis_redactions` event with timestamp, file hash, deletion status.
- **SimilarityMonitor**: after each bar generation, compute n-gram + interval fingerprints; compare against `banned_motifs.json`; if similarity > threshold, flag `legal.alert` event and force re-generation with random seed offset.
- **AuditLogger**: centralized logger writing to `logs/legal/<session>.jsonl` with entries: `{timestamp, sessionId, stage, action, details}`; details include hashed user prompt, sanitized prompt, feature summary, similarity scores.
- **LegalDashboard API**: `/legal/status` returns summary of active sessions, last alerts, redaction counts; consumed by frontend panel.

### Logging Schema Example
```json
{
  "timestamp": "2025-11-24T19:05:12Z",
  "sessionId": "sess_abc123",
  "stage": "prompt_rewrite",
  "action": "replace",
  "details": {
    "hash_original": "b3c1...",
    "sanitized": "High-energy southern rock pentatonic solo",
    "reasons": ["replaced Free Bird", "softened exact-match language"]
  }
}
```

### Hook Points in Codebase
1. `backend/main.py` FastAPI routers → add dependency `LegalPromptMiddleware`.
2. `style_analysis.py` → wrap Essentia/Basic Pitch calls with `LegalInspector` context manager handling temp files + JSON scrub.
3. `music_engine/generator.py` → call `SimilarityMonitor.check(bar_events)` before returning to caller.
4. `logging_utils.py` → extend to support legal log schema + CLI consumption.

With these pieces in place, the legal agent acts like a collaborative bandmate: it rewrites risky directions, certifies analysis outputs, watches for accidental plagiarism, and keeps auditable receipts without throttling creativity.
