import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from sklearn.metrics import auc

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

pallet = [colors['black'], colors['orangered'], colors['grey'], colors['lightgray']]
# pallet = [colors['navy'], colors['orangered'], colors['dodgerblue'], colors['lightsteelblue']]


def compute_rtf_found(edges, seeds, targets, k=1000000):
    found_seeds = []
    found_targets = []
    seeds_count = [0]
    targets_count = [0]
    for i in range(min(len(edges), k)):
        edge = edges[i]
        if edge[0] in seeds and edge[0] not in found_seeds:
            found_seeds.append(edge[0])
            seeds_count.append(seeds_count[-1] + 1)
        elif edge[1] in seeds and edge[1] not in found_seeds:
            found_seeds.append(edge[1])
            seeds_count.append(seeds_count[-1] + 1)
        else:
            seeds_count.append(seeds_count[-1])

        if edge[0] in targets and edge[0] not in found_targets:
            found_targets.append(edge[0])
            targets_count.append(targets_count[-1] + 1)
        elif edge[1] in targets and edge[1] not in found_targets:
            found_targets.append(edge[1])
            targets_count.append(targets_count[-1] + 1)
        else:
            targets_count.append(targets_count[-1])

    return np.array(seeds_count) / len(seeds), np.array(targets_count) / len(targets)


def plot_rtf_found(seeds, targets, our_edges, rwr_edges, pl_edges, el_edges, data):
    our_seeds, our_targets = compute_rtf_found(our_edges, seeds, targets, k=len(pl_edges))
    rwr_seeds, rwr_targets = compute_rtf_found(rwr_edges, seeds, targets, k=len(pl_edges))
    pl_seeds, pl_targets = compute_rtf_found(pl_edges, seeds, targets, k=len(pl_edges))
    el_seeds, el_targets = compute_rtf_found(el_edges, seeds, targets, k=len(el_edges))

    plt.title("number of receptors found for " + data)
    plt.plot([i for i in range(len(pl_seeds))], pl_seeds, color=pallet[0], label="PathLinker")
    plt.plot([i for i in range(len(our_seeds))], our_seeds, color=pallet[1], label="ours")
    plt.plot([i for i in range(len(rwr_seeds))], rwr_seeds, color=pallet[2], label="RWR")
    plt.plot([i for i in range(len(el_seeds))], el_seeds, color=pallet[3], label="EdgeLinker")
    plt.legend()
    plt.savefig("output/receptors/" + data + ".png")
    plt.close()

    plt.title("number of transcription factors found for " + data)
    plt.plot([i for i in range(len(pl_targets))], pl_targets, color=pallet[0], label="PathLinker")
    plt.plot([i for i in range(len(our_targets))], our_targets, color=pallet[1], label="ours")
    plt.plot([i for i in range(len(rwr_targets))], rwr_targets, color=pallet[2], label="RWR")
    plt.plot([i for i in range(len(el_targets))], el_targets, color=pallet[3], label="EdgeLinker")
    plt.legend()
    plt.savefig("output/tfs/" + data + ".png")
    plt.close()

    return our_seeds, our_targets, rwr_seeds, rwr_targets, pl_seeds, pl_targets, el_seeds, el_targets


def compute_node_auprc(edges, pathway_nodes):
    found_nodes = []
    recall = []
    precision = []
    tp = 0
    fp = 0
    for edge in edges:
        if edge[0] not in found_nodes:
            if edge[0] in pathway_nodes:
                tp += 1
            else:
                fp += 1
            found_nodes.append(edge[0])
        if edge[1] not in found_nodes:
            if edge[1] in pathway_nodes:
                tp += 1
            else:
                fp += 1
            found_nodes.append(edge[1])
        recall.append(tp / len(pathway_nodes))
        precision.append(tp / (tp + fp))
    return recall, precision


def compute_pathway_nodes(pathway):
    nodes = []
    for edge in pathway:
        if edge[0] not in nodes:
            nodes.append(edge[0])
        if edge[1] not in nodes:
            nodes.append(edge[1])
    return nodes


def plot_prc(our_recall, our_precision, rwr_recall, rwr_precision, pl_recall, pl_precision, el_recall, el_precision):
    plt.plot(pl_recall, pl_precision, color=pallet[0],
             label="PathLinker " + str(round(auc(pl_recall, pl_precision), 3)))
    plt.plot(our_recall, our_precision, color=pallet[1],
             label="ours " + str(round(auc(our_recall, our_precision), 3)))
    plt.plot(rwr_recall, rwr_precision, color=pallet[2],
             label="RWR " + str(round(auc(rwr_recall, rwr_precision), 3)))
    plt.plot(el_recall, el_precision, color=pallet[3],
             label="EdgeLinker " + str(round(auc(el_recall, el_precision), 3)))
    plt.legend()


def plot_node_auprc(pathway, our_edges, rwr_edges, pl_edges, el_edges, data):
    pathway_nodes = compute_pathway_nodes(pathway)

    our_recall, our_precision = compute_node_auprc(our_edges, pathway_nodes)
    rwr_recall, rwr_precision = compute_node_auprc(rwr_edges, pathway_nodes)
    pl_recall, pl_precision = compute_node_auprc(pl_edges, pathway_nodes)
    el_recall, el_precision = compute_node_auprc(el_edges, pathway_nodes)

    plt.title("node precision recall for " + data)
    plot_prc(our_recall, our_precision, rwr_recall, rwr_precision, pl_recall, pl_precision, el_recall, el_precision)
    plt.savefig("output/node-PRC/" + data + ".png")
    plt.close()

    return our_recall, our_precision, rwr_recall, rwr_precision, pl_recall, pl_precision, el_recall, el_precision, len(
        pathway_nodes)


def compute_overall_recall_precision(recalls, precisions):
    recall = []
    precision = []
    for i in range(max([len(t) for t in recalls])):
        r = 0
        p = 0
        count = 0
        for k in range(len(recalls)):
            if len(recalls[k]) > i:
                count += 1
                r += recalls[k][i]
                p += precisions[k][i]
        if count < len(recalls):
            break
        recall.append(r / count)
        precision.append(p / count)
    return recall, precision


def plot_total_prc(overall_recalls_ours, overall_precisions_ours, overall_recalls_rwr, overall_precisions_rwr,
                   overall_recalls_pl, overall_precisions_pl, overall_recalls_el, overall_precisions_el, name):
    recalls_ours, precisions_ours = compute_overall_recall_precision(overall_recalls_ours, overall_precisions_ours)
    recalls_pl, precisions_pl = compute_overall_recall_precision(overall_recalls_pl, overall_precisions_pl)
    recalls_rwr, precisions_rwr = compute_overall_recall_precision(overall_recalls_rwr, overall_precisions_rwr)
    recalls_el, precisions_el = compute_overall_recall_precision(overall_recalls_el, overall_precisions_el)
    plt.title(name)
    plot_prc(recalls_ours, precisions_ours, recalls_rwr, precisions_rwr, recalls_pl, precisions_pl, recalls_el,
             precisions_el)
    plt.savefig("output/" + name + ".png")
    plt.close()
