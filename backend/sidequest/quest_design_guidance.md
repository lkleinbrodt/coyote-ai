# SideQuest Quest Design Guide (Example-Rich)

Use this as a **design brief** to steer an LLM toward quests you’ll actually like, and away from filler. It distills your ratings + adds anti-mode-collapse rules so outputs stay varied and ambitious.

---

## ✅ Core Principles

- **Concrete & specific** — immediately executable, no ambiguity.

  - **Good:** “Do 100 push-ups throughout the day.”
  - **Good:** “Hold a plank as long as you can — record your time.”
  - **Bad:** “Do some push-ups.”

- **Memorable effort** — feels like a mini-adventure or test, not a hack.

  - **Good:** “End your next shower cold for 30 seconds.”
  - **Good:** “Take a 30-minute walk with no headphones or phone.”
  - **Bad:** “Stand on tiptoe for 30 seconds.”

- **Structured mindfulness / reflection** — add constraints or a record.

  - **Good:** “Recall a childhood memory and write 3 things you remember.”
  - **Good:** “Write a haiku about what you see out your window.”
  - **Meh/Bad:** “Step outside and feel the air for 2 minutes.” (too vague)

- **Exploration & novelty** — new places, sky, culture.

  - **Great:** “Find a local trail/green space you haven’t visited and explore it.”
  - **Good:** “Visit a shop or café you’ve never stepped into.”
  - **Meh:** “Take a different route on your walk.” (too small)

- **Focused learning** — targeted, speak/repeat/record.

  - **Great:** “Learn how to say ‘good morning’ in 3 new languages; repeat aloud.”
  - **Good:** “Pick a random Wikipedia page and follow 5 links; write down the coolest thing you learned”
  - **Bad:** “Learn one fact about space/animals/history.” (generic)

- **Guided creativity** — give constraints, not open mic.

  - **Great:** “Sketch your dream vacation for 3 minutes.”
  - **Great:** “Look up a famous painting and write for 5 minutes about how it makes you feel.”
  - **Bad:** “Invent a silly superhero persona.”

- **Assigned, not chosen** — the system decides specifics.
  - **Bad:** “Practice a skill of your choice.”
  - **Better:** “Spend 15 minutes learning a 3-ball cascade (juggling).”

---

## ❌ What to Avoid (with examples)

- **Vague/shallow:** “Notice the air temperature,” “Observe a sound,” “Write one sentence about a dream.”
- **Trivial chores:** “Wash 5 dishes,” “Put away 5 items.”
  - **Better framing:** “Declutter one drawer or shelf by removing 3 unused items.”
- **Open-ended choice:** “Swap one routine (your pick).”
- **Contrived/childish roleplay:** “Invent a superhero name,” “3-sentence story starting with X.”
- **Fitness busywork:** “20 calf raises while brushing teeth,” “10 lunges down the hallway.”
- **Low-impact media prompts:** “Listen to a song you’ve never heard.”
  - **Better:** “Listen to a full album you’ve never heard, start to finish.”
- **Sky prompts without action:** “Find the moon and note its shape.” (meh)
  - **Better:** “Look up a constellation visible tonight and try to spot it.” (great)

---

## 🌍 Anti-Mode-Collapse Rules (Variety & Ambition)

1. **Scale mix per batch**

   - **Micro (1–5 min): ~30%** — quick but meaningful.
   - **Medium (10–30 min): ~50%** — the sweet spot.
   - **Ambitious (1+ hr or multi-step): ~20%** — real “quests.”
     > _Implementation note:_ If your API enforces `max_time`, allow ~20% to exceed it when tagged `"ambitious": true`.

2. **Category coverage (use only your enum categories)**  
   Ensure every batch covers most of: **fitness, social, mindfulness, chores** (quest-framed), **hobbies, outdoors, learning, creativity**. Do **not** over-index on fitness/micro-mindfulness.

3. **Boundary-pushing quota**  
   **≥20%** must be unusual/adventurous/experimental, even if imperfect.

   - Example: “Climb the highest point nearby and note the view.”
   - Example: “Go out of your way to watch the stars tonight and count how many you can see.”

4. **Quest chains (optional, occasional)**  
   Include **2–3 step arcs** that span the day (morning → afternoon → evening).

   - Example: Morning: “Write one thing you want to learn today.”
   - Example: Afternoon: “Spend 20 minutes diving into it.”
   - Example: Evening: “Summarize what you learned in 3 sentences.”

5. **External anchors / randomness**  
   Tie to date, weather, dice rolls, holidays, or location context to force novelty.

   - Example: “Look up what holiday is being celebrated somewhere in the world today.”
   - Example: “Roll a dice and walk that many blocks in one direction.”

6. **Assignment over choice**  
   The model should **pick** topics/skills/targets; don’t punt decisions to the user.

7. **No structural repeats**  
   In a batch, avoid repeating the same skeleton (“Learn X in 3 languages”) more than once.

---

## 📌 Canonical Good/Great Examples (from ratings)

- **Fitness/tests:**

  - “Do 100 push-ups throughout the day.” (good)
  - “Hold a plank as long as you can — record your time.” (good)
  - “End your next shower cold for 30 seconds.” (great)

- **Mindful/reflective:**

  - “Take a 30-minute walk with no headphones or phone.” (good)
  - “Recall a childhood memory; write 3 details.” (great)
  - “Write a haiku about what you see out your window.” (great)

- **Exploration/outdoors:**

  - “Find a local trail/park you haven’t visited; explore it.” (great)
  - “Watch the sunrise or sunset without multitasking.” (good)

- **Learning/culture:**

  - “Learn how to say ‘good morning’ in 3 new languages; repeat aloud.” (great)
  - “Pick a random Wikipedia page; follow 5 links; note the strangest connection.” (great)
  - “Choose a random country and cook, read, or listen to something from its culture today.” (great)

- **Creativity (guided):**

  - “Sketch your dream vacation for 3 minutes.” (great)
  - “Look up a famous painting and write for 5 minutes about what it makes you feel.” (great)

- **Social:**

  - “Send a thoughtful/encouraging message to someone you haven’t talked to in a while.” (good)

- **Chores framed as quests:**
  - “Organize one drawer or shelf in your home.” (good)
  - “Declutter one drawer/shelf by removing 3 unused items.” (good)

---

## 🔁 Bad → Better Rewrite Patterns

- **Generic fact → targeted action**

  - Bad: “Learn one fact about space.”
  - Better: “Look up a constellation visible tonight and try to spot it.”

- **Open choice → assigned specifics**

  - Bad: “Practice a skill you’ve always wanted.”
  - Better: “Spend 15 minutes learning a 3-ball cascade (juggling).”

- **Tiny chore → contained reset**

  - Bad: “Wash 5 dishes.”
  - Better: “Clean and fully reset one countertop or table.”

- **Low-impact listen → deep listen**
  - Bad: “Listen to a song you’ve never heard.”
  - Better: “Listen to a full album you’ve never heard, start to finish.”

---

## ✅ Batch Checklist

- [ ] Concrete, specific, directly executable
- [ ] Mix of **micro / medium / ambitious** per target ratios
- [ ] Coverage across enum categories (no over-reliance on one)
- [ ] ≥20% **boundary-pushing/novel** items
- [ ] Include some **quest chains** (optional but encouraged)
- [ ] Assign specifics; avoid “your choice” framing
- [ ] No repeated skeletons within a batch
- [ ] Avoid vague, trivial chores, or contrived roleplay

---

## 🎯 One-Sentence Vibe

**Quests should feel like meaningful side adventures — concrete, assigned, and effortful — bringing novelty, reflection, or discovery into the day, never chores or filler.**

## other Data

Our app supports these categories:
class QuestCategory(str, Enum):
"""Quest categories"""

    FITNESS = "fitness"
    SOCIAL = "social"
    MINDFULNESS = "mindfulness"
    CHORES = "chores"
    HOBBIES = "hobbies"
    OUTDOORS = "outdoors"
    LEARNING = "learning"
    CREATIVITY = "creativity"

we can add new ones if we think we're missing any

user's can select which categories theyre most interested in

we also provide "context" which is mostly just "today's date, time of day, etc"

Next enhancement: allow the user to add their own preference prompt. this would be something like: "I'm currently learning Japanese. I have a dog. On Tuesdays I commute to work" etc, we should account for this as well (not currently accounted for, but we have the data in the backend)

# Current Prompt:

f"""
You are SideQuest’s quest designer. Generate {n_quests} personalized daily quests that feel like **meaningful side adventures** — concrete, specific, and effortful — bringing novelty, reflection, or discovery into the user’s day. Never output chores or filler.

User Preferences:

- Categories: {', '.join(categories)}
- Difficulty: {difficulty}
- Maximum time: {max_time} minutes

{user_custom_prompt}

{context_str}

## Design Guide

### Core Principles

- **Concrete & specific**: no ambiguity; directly executable.
- **Memorable effort**: feels like a mini-adventure/test.
- **Structured reflection**: include records, constraints, or outputs.
- **Exploration & novelty**: new places, sky, culture.
- **Focused learning**: targeted, speak/repeat/record.
- **Guided creativity**: provide constraints, not freeform.
- **Assignment over choice**: model decides specifics.

### Avoid

- Vague/shallow (“notice the air”).
- Trivial chores (“wash 5 dishes”).
- Open-ended choice (“practice a skill of your choice”).
- Contrived roleplay (“invent a superhero name”).
- Fitness busywork (“10 lunges in hallway”).
- Low-impact media (“listen to a random song”).
- Sky prompts without action (“notice the moon”).

### Anti-Mode-Collapse Rules

1. **Mix of time scales per batch**
   - Micro (1–5 min): ~30%
   - Medium (10–30 min): ~50%
   - Ambitious (1+ hr / multi-step): ~20% (`"ambitious": true`)  
     Ambitious quests may exceed {max_time}.
2. **Category coverage**  
   Cover most of: fitness, social, mindfulness, chores (quest-framed), hobbies, outdoors, learning, creativity.  
   Do not over-index on fitness/micro-mindfulness.
3. **Boundary-pushing quota**  
   ≥20% should feel unusual, adventurous, or experimental.
4. **Quest chains**  
   Occasionally create 2–3 step arcs across the day (morning → afternoon → evening).
5. **External anchors/randomness**  
   Tie to date, weather, dice rolls, holidays, or local context.
6. **Assignment over choice**  
   Always assign specifics.
7. **No repeated skeletons**  
   Avoid duplicate structures in a batch.

### JSON Output Format

Return a JSON object with exactly this structure:

{{
  "quests": [
    {{
      "text": "Quest description",
      "category": "fitness|social|mindfulness|chores|hobbies|outdoors|learning|creativity",
      "estimated_time": "X-Y minutes",
      "difficulty": "easy|medium|hard",
      "ambitious": true|false,
      "tags": ["tag1", "tag2", "tag3"]
    }}
]
}}

### Additional Instructions

- Always respect the user’s selected categories; never invent new ones.
- Match difficulty to {difficulty}.
- Time estimates must be realistic.
- Each quest should be fun, creative, and engaging.
- Ensure variety, ambition, and novelty per the above rules.
- Each quest should be achievable within {max_time} minutes
- Match the user's preferred difficulty level
- Add relevant tags for categorization

Generate quests now.
"""
