import uuid
import json

from app.agents.main_graph import main_graph

from questionnaire import BIG5, PROFILE


thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": 24}, "recursion_limit":100}

if not main_graph.get_state(config).values:
    output = main_graph.invoke(
        {
            "profile": json.dumps(PROFILE, ensure_ascii=True, indent=1),
            "big5": json.dumps(BIG5, ensure_ascii=True, indent=1),
            "genre": "steampunk",
            "level": "HighSchool(Grades10-12/Ages15-18)",
        },
        config,
    )
    print("\nFirst Prologue draft is generated")

    user_feedback_list = [
        "It's too grandiose. I want the prologue to start from a more normal and mundane life.",
        "Make the main character super poor and miserable.",
        "Don't use the detail of me in a ackward way. For example, the detail of the brown horn-rimmmed glasses is not necessary in this prologue.",
    ]

    for i, user_feedback in enumerate(user_feedback_list):
        main_graph.update_state(
            config,
            {
                "user_feedback": user_feedback,
            },
            as_node="get_feedback_from_user",
        )
        output = main_graph.invoke(None, config)
        print(f"==>> Completed {i+1} / {len(user_feedback_list)} Feedback")

    while True:
        user_feedback = input("\nEnter a feedback:")
        if user_feedback == "q":
            break
        main_graph.update_state(
            config,
            {
                "user_feedback": user_feedback,
            },
            as_node="get_feedback_from_user",
        )
        output = main_graph.invoke(None, config)

    main_graph.update_state(
            config,
            {
                "is_prologue_completed": True,
            },
            as_node="get_feedback_from_user",
        )
    main_graph.invoke(None, config)
else:
    print("Prologue is already completed")
    main_graph.invoke(None, config)

while True:
    user_choice = input("Enter the number of the choice:")

    if user_choice == "q":
        break

    try:
        user_choice_int = int(user_choice)
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        continue

    state = main_graph.get_state(config, subgraphs=True)
    subgraph_config = state.tasks[0].state.config  # config of the subgraph

    main_graph.update_state(
        subgraph_config,
        {
            "user_choice": user_choice_int,
        },
    )
    state = main_graph.get_state(config, subgraphs=True)

    main_graph.invoke(None, config)
