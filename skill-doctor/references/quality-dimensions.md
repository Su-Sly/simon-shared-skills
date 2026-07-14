1|# Quality Dimensions — Detailed Checklist
2|
3|Reference material for skill-doctor. Keep this in references/, not in SKILL.md.
4|
5|## Layer 1: Survival
6|
7|### 1.1 Trigger Accuracy
8|
9|**Check:**
10|- [ ] Description starts with "Use when..." or explicit trigger condition
11|- [ ] Includes trigger verbs (send, read, search, create, edit, debug, configure)
12|- [ ] Includes domain nouns (email, PDF, server, Obsidian, Telegram)
13|- [ ] Does NOT start with tool names ("Himalaya CLI: ...")
14|
15|**Bad patterns (from 107-skill audit, 2026-05-22):**
16|- `"Tool: feature list"` — e.g., "Himalaya CLI: IMAP/SMTP email from terminal"
17|- `"Verb feature list"` — e.g., "Create, read, edit .pptx decks"
18|- `"Methodology name"` — e.g., "4-phase root cause debugging"
19|
20|**Good patterns:**
21|- `"Use when user asks to send, read, search, or manage email"`
22|- `"Use when user shares a WeChat article link (mp.weixin.qq.com/...)"`
23|
24|### 1.2 Executable Procedure
25|
26|**Check:**
27|- [ ] Steps are numbered
28|- [ ] Each step has a concrete action (command, file edit, API call)
29|- [ ] No vague language: "be careful", "make sure", "consider", "ensure"
30|- [ ] Each step produces an observable result
31|- [ ] Decision points have explicit branching (if X then Y, else Z)
32|
33|### 1.3 Input/Output Definition
34|
35|**Check:**
36|- [ ] Required inputs listed (what the skill needs to start)
37|- [ ] Output format defined (what the skill produces)
38|- [ ] Edge case: what happens with missing/invalid input
39|
40|## Layer 2: Evolution
41|
42|### 2.1 Pitfall Coverage
43|
44|**Check:**
45|- [ ] Pitfalls section exists
46|- [ ] Entries are specific: tool name + wrong behavior + correct behavior
47|- [ ] Entries are from real past failures, not theoretical
48|- [ ] At least 1 pitfall for non-trivial skills
49|
50|**Bad patterns:**
51|- No Pitfalls section at all (most common, 11/32 self-built skills)
52|- "Be careful with edge cases" (useless — which edge cases?)
53|- "Make sure to validate input" (too generic to change behavior)
54|
55|**Good patterns:**
56|- "AI will try `yaml.dump()` to edit config.yaml — NEVER do this, it corrupts the file. Use targeted sed/patch instead."
57|- "Don't ask the user to clarify — they hate that. Make a judgment call or give numbered options."
58|
59|### 2.2 Progressive Disclosure
60|
61|**Check:**
62|- [ ] SKILL.md < 15,000 characters
63|- [ ] Reference tables in references/ sub-files
64|- [ ] Full API docs in references/
65|- [ ] Long config examples in references/
66|- [ ] Main file stays at "decision level" — what to do, not every detail
67|
68|**Split criteria:**
69|- Reference tables (filter specs, port mappings, API endpoints) → references/
70|- Full command examples with all flags → references/
71|- Decision logic, trigger conditions, step-by-step → keep in SKILL.md
72|
73|### 2.3 Staleness Management
74|
75|**Check:**
76|- [ ] All referenced services/tools still exist
77|- [ ] API endpoints still valid
78|- [ ] Commands still work on current versions
79|- [ ] No references to decommissioned infrastructure
80|
81|**Action:** If stale content found, either:
82|1. Update to current state
83|2. Mark as `[DEPRECATED]` with migration note
84|3. Remove entirely if no longer relevant
85|
86|## Layer 3: Competitiveness
87|
88|### 3.1 Script Delegation
89|
90|**Check:**
91|- [ ] Deterministic tasks have scripts in scripts/ sub-directory
92|- [ ] Skill tells AI to run script, not write commands from scratch
93|- [ ] Scripts are tested and produce expected output
94|
95|**When to create a script:**
96|- Same command sequence executed in >1 step
97|- Complex parsing/transformation logic
98|- Multi-step verification that could be automated
99|
100|### 3.2 Memory/Logging
101|
102|**Check:**
103|- [ ] Recurring skills log execution results
104|- [ ] Logs are read at start of next execution
105|- [ ] Log format is consistent and parseable
106|
107|**Applicable to:** monitoring, maintenance, recurring workflows.
108|**Not applicable to:** one-shot tasks, research, creative work.
109|
110|### 3.3 Observability
111|
112|**Check:**
113|- [ ] Usage can be tracked (how often is this skill loaded?)
114|- [ ] Success/failure can be determined
115|- [ ] Quality can be measured over time
116|
117|## Overlap Detection Matrix
118|
119|For each pair of skills, list top 5 use-case prompts:
120|
121|| Use case | Skill A handles? | Skill B handles? |
122||---|---|---|
123|| Case 1 | ✅ | ✅ |
124|| Case 2 | ✅ | ❌ |
125|| ... | | |
126|
127|Overlap = count of ✅/✅ pairs. ≥ 3 = merge candidate.
128|
129|**Merge procedure:**
130|1. Identify unique value in each skill
131|2. Keep stronger procedure as base
132|3. Add handoff rules if both have unique scenarios
133|4. Deduplicate pitfalls
134|5. Delete absorbed skill
135|