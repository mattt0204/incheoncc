import os
import random

user_agent_list_txt_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "user_agent_list.txt"
)


def get_random_user_agent():
    lines = open(user_agent_list_txt_path, "r").read().splitlines()
    return random.choice(lines)
