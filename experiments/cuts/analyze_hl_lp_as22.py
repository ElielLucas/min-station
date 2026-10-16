"""AS22 paired LP gate, with strictly descriptive AS20 cross-campaign comparison.

Gurobi wall times from different experimental runs are exploratory, never a
proof of speedup. Structural caps and UNKNOWN prevent negative conclusions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_hl_lp import analyze as analyze_as20


def analyze(plan, manifest, rows):
    base = analyze_as20(plan, manifest, rows)
    base['schema_version'] = 'AS22-HL-ANALYSIS-v1'
    base['stage'] = 'AS22'
    base['method'] = 'general_nonnegative_hl_complete_projection_rational_certification'
    base['note'] = ('Only complete physical pattern classifications certify finite '
                    'projection; numerical LP proposes nonnegative coefficients, '
                    'rationalized row and exact finite minimum beta certify the cut. '
                    'UNKNOWN, caps, no support and censures are inconclusive. '
                    'A positive preliminary gate requires independent review; no MIP.')
    # AS20's analysis treats additional cap statuses as partial only via
    # PARTIAL_BUDGET. Our separator reports PARTIAL_BUDGET for any cap.
    for c in base['cases']:
        c['interpretation'] = ('not measured' if not c['paired_optimal']
             else 'incomplete' if c['screen_incomplete'] else 'bounded screen')
    return base
