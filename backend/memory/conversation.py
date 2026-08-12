memory = {}


def load(user_id):

    return memory.get(user_id)

def save(user_id, requirements):

    memory[user_id] = requirements