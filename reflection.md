# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design represents the main components of PawlPal+ and how they interact, showing the relationships between owners, pets, and care tasks.

- What classes did you include, and what responsibilities did you assign to each?
Owner: Stores owner information and manages their pets and availability.
Pet: Stores pet information and keeps track of its care tasks.
Task: Represents a care activity, including its duration, priority, scheduled time, and recurrence.
Scheduler: Sorts tasks, detects scheduling conflicts, and generates an organized daily schedule.
CarePlan: Stores the final schedule, including scheduled and skipped tasks and explanations for scheduling decisions.

**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
I adjusted the design so that ownership and task assignment are validated carefully rather than letting the object drift out of sync.
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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
