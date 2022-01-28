import dataclasses
import random
from numpy.random import choice
from typing import Tuple, List

from algorithms import CaseRecommendation
from db.sqlalchemy.models import Court
from graph import CitationNetwork


@dataclasses.dataclass
class RecallResult:
    case: int
    num_trials: int
    top1: int
    top5: int
    top20: int


@dataclasses.dataclass
class OverallRecallResult:
    case_results: List[RecallResult]
    num_trials: int
    overall_top1: float
    overall_top5: float
    overall_top20: float


class CaseRecall:
    citation_network: CitationNetwork

    def __init__(self, citation_network: CitationNetwork):
        self.citation_network = citation_network
        self.recommendation = CaseRecommendation(self.citation_network)

    def case_recall(self, cases: (Tuple[int], int), court: Tuple[Court], num_trials: int, same_court: bool):
        if isinstance(cases, int):
            # cases will be selected in proportion to how often they're mentioned --- this seems good
            cases = choice(self.citation_network.network_edge_list.edge_list, size=cases)
        overall_top1 = 0
        overall_top5 = 0
        overall_top20 = 0
        recall_results = []
        for c in cases:
            md = self.citation_network.network_edge_list.node_metadata[c]
            neighbors = list(self.citation_network.network_edge_list.edge_list[md.start:md.end])
            top1 = 0
            top5 = 0
            top20 = 0
            for i in range(num_trials):
                removed_idx = random.randrange(len(neighbors))
                neighbors[removed_idx], neighbors[-1] = neighbors[-1], neighbors[removed_idx]
                removed = neighbors.pop()
                same_court = (
                    self.citation_network.network_edge_list.node_metadata[removed].court,) if same_court else ()
                recommendations = list(
                    self.recommendation.recommendations(frozenset(neighbors), 20, courts=frozenset(court + same_court),
                                                        ignore_opinion_ids=frozenset([c]), max_num_steps=100_000).keys())
                if removed in recommendations:
                    top20 += 1
                if removed in recommendations[:5]:
                    top5 += 1
                if removed in recommendations[:1]:
                    top1 += 1
                neighbors.append(removed)
            overall_top1 += top1
            overall_top5 += top5
            overall_top20 += top20
            recall_results.append(RecallResult(c, num_trials, top1, top5, top20))
            print(f"For case {c} after {num_trials} trials:\n\ttop1: {top1}\n\ttop5: {top5}\n\ttop20: {top20}")
        overall_top1 = 100 * overall_top1 / (num_trials * len(cases))
        overall_top5 = 100 * overall_top5 / (num_trials * len(cases))
        overall_top20 = 100 * overall_top20 / (num_trials * len(cases))
        # TODO: Remove print statements and use returned dataclasses to output results from the CLI
        print(
            f"For {len(cases)} cases after {num_trials} trials each:\n\ttop1: {overall_top1}%\n\ttop5: {overall_top5}%\n\ttop20: {overall_top20}%")
        return OverallRecallResult(recall_results, num_trials, overall_top1, overall_top5, overall_top20)
