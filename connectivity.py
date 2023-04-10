import networkx as nx
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

from file_methods import read_source_and_destinations, read_nodes

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

datas = ["Alpha6Beta4Integrin", "AndrogenReceptor", "BCR", "BDNF", "CRH", "EGFR1", "FSH", "Hedgehog", "IL1",
         "IL2", "IL3", "IL4", "IL5", "IL6", "IL9", "IL-7", "KitReceptor", "Leptin", "Notch", "Oncostatin_M",
         "Prolactin", "RANKL", "TCR", "TGF_beta_Receptor", "TNFalpha", "TSH", "TSLP", "TWEAK", "Wnt"]

# defining the bounds for which we want to compute the connectivity
bounds = [100 * (i+1) for i in range(20)]
pallet = [colors['dodgerblue'], colors['forestgreen'], colors['limegreen'], colors['springgreen'], colors['turquoise'],
          colors['deepskyblue'], colors['dodgerblue'], colors['blue']]

connected_pairs = [[] for _ in range(len(bounds))]

for data in datas:
    our_pathway = "results/" + data + "edges-ours.txt"

    rtf_path = "data/NetPath/" + data + "-nodes.txt"
    nodes = read_nodes("data/nodes_map.txt")
    # reading seeds and targets
    seeds, targets = read_source_and_destinations(rtf_path, nodes)

    # defining a graph for each bound
    G = [nx.Graph() for _ in range(len(bounds))]

    # reading the pathway generated by our algorithm
    edges = []
    with open(our_pathway, 'r') as f:
        for line in f:
            sp = line.split()
            edges.append([int(sp[0]), int(sp[1])])

    connected_pairs_data = [0 for _ in range(len(bounds))]
    for i in range(len(bounds)):
        for j in range(bounds[i]):
            G[i].add_edge(edges[j][0], edges[j][1])

        for seed in seeds:
            if G[i].has_node(seed):
                descendants = nx.algorithms.descendants(G[i], seed)
                for target in targets:
                    if target in descendants:
                        connected_pairs_data[i] += 1

        connected_pairs_data[i] /= len(seeds) * len(targets)

    for i in range(len(bounds)):
        connected_pairs[i].append(connected_pairs_data[i])
    print(connected_pairs_data)

plt.plot(bounds, [sum(connected_pairs[i]) / len(datas) for i in range(len(bounds))], color=pallet[0])
# plt.xticks([j for j in range(len(datas))], datas, rotation=90)
plt.ylim(bottom=0)
plt.title("percentage of receptors and transcription factors connected to each other")
plt.savefig("output/connectivity_low.png")
plt.close()
