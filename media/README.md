# Walkthrough build

The walkthrough is a concise leadership story modeled on the visual rhythm of
the Cowork Value Intelligence video. It is not a page-by-page inventory.

## Story arc

1. Introduce the testing, data-free Adoption template.
2. Start with the business decision.
3. Read latest-week reach, recurrence, intensity, and maturity together.
4. Test whether use returns across the latest 12 active weeks.
5. Compare adoption patterns across available organization attributes.
6. Understand usage consistency and delegation depth.
7. Identify potential champions responsibly.
8. Keep observed activity and assisted-time assumptions separate.
9. Find the work categories and skills worth enabling.
10. Explain the momentum score, weights, caps, and guardrails.
11. Trace definitions and dependencies before acting.
12. Connect approved exports and build an evidence-aware enablement plan.

## Build

Requirements:

- Windows PowerShell or PowerShell 7
- Python 3.10+
- Pillow
- `edge-tts`
- FFmpeg and FFprobe on `PATH`

Run from the repository root:

```powershell
.\media\build_walkthrough.ps1
```

The build reads `walkthrough_segments.json`, creates temporary 1920x1080 story
frames, synthesizes one continuous neural narration per beat, generates aligned
subtitles, and writes:

- `Cowork-Adoption-Intelligence-Walkthrough.mp4`
- `Cowork-Adoption-Intelligence-Walkthrough.srt`
- `Cowork-Adoption-Intelligence-Walkthrough-transcript.md`
- `Cowork-Adoption-Intelligence-Walkthrough-timeline.json`

Generated frames under `media\composed` are ignored by Git.

## Release targets

- 1920x1080
- 30 fps
- H.264 video
- AAC, 48 kHz stereo audio
- warm, conversational `en-US-AvaNeural` narration at `+5%` rate
- approximately 3 minutes 36 seconds
- approximately -18 LUFS integrated loudness
- 0.8-second pauses between story beats
- visible testing-template and approved-export language
- no customer identity, tenant URL, or customer export
- only fabricated report screenshots
