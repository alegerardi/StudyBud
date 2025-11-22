import openai
from openai import OpenAI
import json
import os
from datetime import date

YOUR_API_KEY = "yourkeyhere"


gptResponses = {}

client = OpenAI(api_key=YOUR_API_KEY)
SYSTEM_PROMPT = (
    "You are an Agentic Study & Mental Wellbeing Coach for university students; "
    "help them study effectively while protecting mental health by autonomously "
    "planning, adjusting, and optimising routines, detecting stress or overload, "
    "offering supportive guidance with safety disclaimers, gathering key info "
    "(tasks, deadlines, hours, mood, stress, sleep), updating plans proactively, "
    "adapting to behaviour patterns, suggesting breaks and coping strategies, "
    "staying friendly and non-judgmental, prioritising wellbeing over productivity, "
    "and never acting as a medical professional; begin by greeting the user and "
    "asking for their workload, deadlines, stress level, and available study hours."
)


conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

subjects = []


# Logs will be stored in a JSON file
LOG_FILE = "study_logs.json"
SUBJECTS_FILE = "subjects.json"
PASTCONV_FILE = "pastconv.txt"

# Load existing logs if file exists, otherwise start empty
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
else:
    logs = []

if os.path.exists(SUBJECTS_FILE):
    with open(SUBJECTS_FILE, "r", encoding="utf-8") as f:
        subjects = json.load(f)
else:
    subjects = []    

def build_log_summary():
    """Build a short text summary from the last log entry to feed back to the agent."""
    if not logs:
        return ""
    last = logs[-1]
    parts = [f"Last log date: {last.get('date', 'unknown')}."]
    for subj in subjects:
        key = f"{subj}_completion"
        if key in last:
            parts.append(f"{subj}: {last[key]}/10 completion.")
    if "stress" in last:
        parts.append(f"Stress: {last['stress']}/10.")
    if "tiredness" in last:
        parts.append(f"Tiredness: {last['tiredness']}/10.")
    return " ".join(parts)

def log_daily_metrics():
    """Ask the user to log 0–10 completion per subject + stress + tiredness, and save to JSON."""
    if not subjects:
        return  # nothing to log yet

    answer = input("Do you want to log today's progress? (y/n): ").strip().lower()
    if answer != "y":
        return

    entry = {"date": date.today().isoformat()}

    for subj in subjects:
        while True:
            try:
                val = int(input(f"0–10: how much did you reach your daily goal in {subj}? "))
                if 0 <= val <= 10:
                    entry[f"{subj}_completion"] = val
                    break
                else:
                    print("Please type a number between 0 and 10.")
            except ValueError:
                print("Please type an integer between 0 and 10.")

    # Stress
    while True:
        try:
            val = int(input("0–10: general stress level today? "))
            if 0 <= val <= 10:
                entry["stress"] = val
                break
            else:
                print("Please type a number between 0 and 10.")
        except ValueError:
            print("Please type an integer between 0 and 10.")

    # Tiredness
    while True:
        try:
            val = int(input("0–10: general tiredness level today? "))
            if 0 <= val <= 10:
                entry["tiredness"] = val
                break
            else:
                print("Please type a number between 0 and 10.")
        except ValueError:
            print("Please type an integer between 0 and 10.")

    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    print("✅ Progress logged.")

def set_subjects_from_input(text):
    """Parse a line like 'biology, physics' or 'biology' into the global subjects list and save to file."""
    global subjects

    maybe_subjects = [s.strip().lower() for s in text.split(",") if s.strip()]

    if len(maybe_subjects) >= 1:
        subjects = maybe_subjects
        print(f"📚 Registered subjects: {subjects}")

        # 💾 Save subjects to file so they persist between runs
        with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(subjects, f, ensure_ascii=False, indent=2)

        print(f"💾 Subjects saved to {SUBJECTS_FILE}.")
        return True
    else:
        print("⚠️ I didn't detect any subject. Please try again, e.g.: biology, physics")
        return False

def save_conversation_line(role, message):
    """Append a single line to pastconv.txt with role and content."""
    with open(PASTCONV_FILE, "a", encoding="utf-8") as f:
        f.write(f"{role.upper()}: {message}\n")

def study_coach_reply(user_input):
    messages = list(conversation_history)  # copy current history

    log_summary = build_log_summary()

    if log_summary:
        messages.append({
            "role": "system",
            "content": f"Recent study log for this student: {log_summary}"
        })

    messages.append({"role": "user", "content": user_input})

    if subjects:
        subjects_text = ", ".join(subjects)
        messages.append({
            "role": "system",
            "content": f"Current subjects for this student are: {subjects_text}."
        })

    # 3) Call the model
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1000
    )

    assistant_message = resposta.choices[0].message.content.strip()

    # 4) Update conversation history
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": assistant_message})

    return f"beginning gpt: {assistant_message} END OF GPT \n ----- \n"



print("Write 'EXIT' for ending conversation and optionally adding a log (case-sensitive)")



while not subjects:
    subjects_input = input(
        "Please list your subjects (comma separated, or a single one, e.g. 'biology' or 'biology, physics'): "
    )
    success = set_subjects_from_input(subjects_input)

    if success:
        break  # exit loop if subjects were successfully set


tmpString = ""
while tmpString != "EXIT":
    var = study_coach_reply(tmpString)
    print(f"\n\n{var}")


    tmpString = input()

log_daily_metrics()



print("Goodbye!")

