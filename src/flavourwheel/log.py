def search_adj2noun_log(commands, token, adj2noun_log):
    for i, v in enumerate(adj2noun_log):
        for j in v:
            if token in list(j.items())[0][1]:
                print(j)
                print("")
                print(commands[i])