memory_store = {}

def save_memory(user, message, response):
    if user not in memory_store:
        memory_store[user] = []

    memory_store[user].append((message, response))

def get_memory(user):
    return memory_store.get(user, [])

def get_last_interest(user):
    if user in memory_store:
        for msg, _ in reversed(memory_store[user]):
            if "cse" in msg.lower():
                return "CSE"
            elif "mba" in msg.lower():
                return "MBA"
    return None