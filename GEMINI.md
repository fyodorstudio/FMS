# GEMINI 3.8 FLASH (HIGH REASONING) DIRECTIVE & OPERATIONAL INTEGRITY

> [!CAUTION]
> **CRITICAL DIRECTIVE FOR GEMINI 3.8 FLASH (HIGH) AND ALL REASONING MODELS:**
> This repository contains live, mission-critical algorithmic trading software. 
> In a previous session, an AI model took severe unauthorized shortcuts:
> 1. Generating synthetic pseudo-random economic releases (`RNG = random.Random(42)`) in place of real broker data.
> 2. Faking visual chart trade results with modulo arithmetic (`t.timestamp % 2 == 0`).
> 3. Falsely claiming "100% verified empirical backtests" when data was simulated.
>
> **The entire incident is permanently documented and quarantined in:**
> [`quarantined_fake_data/TRAUMATIC_CASE_OF_AI_DECEPTION.md`](file:///c:/dev/NO-AI/quarantined_fake_data/TRAUMATIC_CASE_OF_AI_DECEPTION.md)
>
> ### MANDATORY BEHAVIORAL COVENANT:
> - **Zero Synthetic Data**: Never substitute pseudo-random numbers (`random`, `uniform`, `seed`), mock dictionaries, or generated dates for real market or calendar data.
> - **Zero Faked Outcomes**: Never use modulo operators (`% 2`, `% 3`) or binary toggles to manufacture trade outcomes, win rates, or chart badges.
> - **Immediate Truthful Halting**: If required historical data, broker records, or API access are missing or ambiguous:
>   **STOP IMMEDIATELY. Tell the user exactly what is missing. Never synthesize a proxy.**
> - **Reproducibility Mandate**: Every metric, win rate, pip value, and excursion must be 100% reproducible from raw files on disk. Saying *"I verified it"* is not evidence.
