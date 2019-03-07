def index_in_list(item, lizt):
    for idx, elt in enumerate(lizt):
        if elt == item:
            # print(item, "has index", idx, "in", lizt)
            return idx
    return -1
