# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design represents the main components of PawlPal+ and how they interact, showing the relationships between owners, pets, and care tasks.

- What classes did you include, and what responsibilities did you assign to each?
Owner: Stores owner information and manages their pets and availability.
Pet: Stores pet information and keeps track of its care tasks.
Task: Represents a care activity, including its title, due date and time, frequency, and completion status.
Scheduler: Sorts tasks, detects scheduling conflicts, and generates an organized daily schedule.
CarePlan: Groups a pet's tasks and keeps them linked to the right pet and owner.

**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
I adjusted the design so that ownership and task assignment are validated carefully rather than letting the object drift out of sync. I also dropped duration and priority from Task, and added sorting, filtering, conflict detection and recurrence methods to Scheduler, which the final UML now shows.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Time, completion status and recurrence
- How did you decide which constraints mattered most?
Time is first because a pet-care routine is mostly about doing the right thing at the right time. Recurrence came second because it removes the most repeated manual work
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My conflict detection only flags tasks that start exactly at the smae time, it doesn't catch overlapping ranges.
- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable here because a household has only a handful of tasks per day, and most clashes happen when two things are deliberately booked for the same time.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used it to review pawpal_system.py and list behaviors to verify. It also listed edge cases, wrote the pytest suite, connected the Streamlit UI to the Scheduler, updated the UML, and drafted the README
- What kinds of prompts or questions were most helpful?
Specific, scoped ones, like "list 3-5 core behaviors to verify" or "what edge cases matter for sorting and recurring tasks?". Asking for the happy path and the edge cases separately gave me a checklist I could turn straight into tests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I accepted the AI's list of edge cases and test drafts, but not its first UI version. It left a pointless `st.rerun() if False else None` line, and the schedule table did not refresh after "Mark complete". I had it switch to a button callback so the table updates. I also did not keep the README's `pytest --cov` command, because pytest-cov was not installed, and I kept the exact-start-time conflict rule instead of adding durations.
- How did you evaluate or verify what the AI suggested?
I ran the 16 tests, ran main.py and compared its output to what I expected, and drove the Streamlit app with Streamlit's test harness (two clashing tasks, then mark complete) to check the warnings and the next occurrence.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Sorting (order, date before time, queue not changed, empty queue). Recurrence (daily +1 day, weekly +7 days, one-off, no duplicates, month boundary, unknown id). Conflict detection (same pet, different pets, near-miss times, completed tasks, empty queue). A pet with no tasks.

- Why were these tests important?
These are the core scheduling rules, and each fails in a way that would mislead an owner, like a missed task or a false alarm.

**b. Confidence**

- How confident are you that your scheduler works correctly?
4 out of 5. All 16 tests pass and the three main behaviors are covered.

- What edge cases would you test next if you had more time?
 filter_tasks, remove_pet and the owner/pet/care plan linking, whether completed tasks should appear in "due today", and tasks with overlapping durations.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The scheduling logic. Sorting, filtering, conflict detection and recurrence work together and are tested. The same methods feed both main.py and the UI.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
Add a duration to tasks so overlaps can be detected, and add priority back. Also decide how completed tasks should appear in the daily schedule, and rewrite the conflict warnings in friendlier wording.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Design the data and the rules first, then test them before building the UI. The AI was fastest when I gave it a small, clear task, and I still had to run the code to know it worked.
