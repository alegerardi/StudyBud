Study Coach Prototype – Simple README

How to Run

1.  Install dependencies:

        pip install openai

2.  Add your OpenAI API key inside the script or set it as an
    environment variable.

3.  Run the program.

       

What It Does

-   Acts as a study and wellbeing assistant using an OpenAI model.
-   Asks for your subjects, tracks progress, stress, and tiredness.
-   Saves logs in JSON files.
-   Lets you chat with the assistant until you type EXIT.

Files Created

-   subjects.json – stores your subjects.
-   study_logs.json – daily progress logs.
-   pastconv.txt – conversation history log. (for future use)

Libraries Used

-   openai (official OpenAI Python client)
-   Python standard libraries: json, os, datetime

Custom Code Logic

-   Loads/saves subjects and logs.
-   Sends conversation history and recent progress to the OpenAI model.
-   Asks you to log daily progress after exiting.
