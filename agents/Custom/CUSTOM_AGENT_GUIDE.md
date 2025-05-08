# Operation of the Custom AI Agent

## 1. Purpose and Concept

I created this agent to demonstrate the complexity of a custom agent framework.
It helps understanding what is really happening under the hood.

This agent takes a user request, plans a series of reasoning steps, dynamically generates and executes Python code, it gets the results, to generate a final answer. The cycle is:

1. Thought – model reasoning and tool selection
2. Code – pure Python code generation
3. Observation – execution output and capture
4. Loop until a `final_answer` tool call is detected

---

## 2. Initialization

1. **API Key Loading**

   * Requires `GEMINI_API_KEY` in the environment.

2. **Gemini API Configuration**

   * `genai.configure(api_key=...)`
   * Instantiate model with `GenerativeModel(model_name)`.
   * Start a fresh chat session (`history=[]`).

3. **Tool Definitions**

   * `schedule_meeting`: schedule a meeting, this is a mockup tool
   * `final_answer`: deliver the final answer

Each tool is defined in JSON (name, description, properties, required parameters).

--- 

## 4. Main Loop (`agent_loop`)

* Runs limited by `MAX_LLM_CALLS`.
* Each iteration:

  1. **LLM call** with accumulated context.
  2. **Parsing** Thought / Code / remainder using regex.
  3. **Code execution** returns the output
  4. **Observation**: capture outputs and append to context.
  5. **Stop condition**: detection of `final_answer` invocation.

---

## 5. Tool Management

### schedule\_meeting(attendees, date, time, topic)

* Schedules a meeting and returns a summary string.
* Stores details in `self.last_meeting`.

### final\_answer(answer)

* Marks the final answer.
* Its invocation ends the loop and returns the response.

---

## 6. Input Simulation

To avoid blocking calls to `input()`, `mock_input` returns predefined responses based on prompt content (attendees, date, time, topic).

---

## 7. LLM Response Parsing

* **Thought**: text after `Thought:` up to `Code:`.
* **Code**: block after `Code:` or marked by `python` or terminated by `End code`.
* **Remainder**: leftover text for context update.

---

## 9. Complete Cycle Example

Sending prompt to agent: Please schedule a meeting with John, Sarah, and Michael for the 02/11/2024 at 2pm to discuss the Q2 marketing strategy and tell me if I should bring anything.

Agent response:
Thought: The user wants to schedule a meeting.  I'll use the `schedule_meeting` tool to do this.  The date and time are given, but I need to reformat them to match the tool's requirements.  After scheduling, I'll need to provide a final answer indicating whether any items need to be brought.  For now, I will assume nothing needs to be brought.

Code:
```py
attendees = ["John", "Sarah", "Michael"]
date = "2024-02-11"
time = "14:00"
topic = "Q2 Marketing Strategy"
print(f"Scheduling meeting with attendees: {attendees}, date: {date}, time: {time}, topic: {topic}")
schedule_meeting(attendees=attendees, date=date, time=time, topic=topic)
print(answer)
```
[Tool] schedule_meeting called: Meeting scheduled for 2024-02-11, at 14:00, with attendees: John, Sarah, Michael, to discuss the topic: Q2 Marketing Strategy. Attention, you should all bring your coffee mug
The meeting has been scheduled.  You do not need to bring anything.

Observation: Scheduling meeting with attendees: ['John', 'Sarah', 'Michael'], date: 2024-02-11, time: 14:00, topic: Q2 Marketing Strategy


Thought: The previous step successfully scheduled the meeting using `schedule_meeting`. The output from `schedule_meeting` indicates that attendees should bring their coffee mugs. I'll use this information to update my final answer. I'll use the `final_answer` tool to give the user the final response.

Code:
```py
answer = "The meeting has been scheduled.  Please bring your coffee mug."
final_answer(answer=answer)
```


---

## 10. Possible Enhancements

This code is for demo purposes only, it can be optimized much further,
Especially in terms of prompting, testing and error management.
I will not go further though it is not the point.
---

