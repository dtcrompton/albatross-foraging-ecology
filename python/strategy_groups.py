"""
Display names and colours for the three k-means foraging-strategy groups.

Shared by the Phase 3 figure and the Phase 4 map so their colours cannot drift
apart. The groups come from foraging-strategy metrics only and use no fishing data.
"""

# Legacy risk_label value -> group letter
GROUP_FROM_RISK_LABEL = {'Low risk': 'A', 'Medium risk': 'B', 'High risk': 'C'}

# Okabe-Ito blue, orange and reddish purple: colour-blind safe, no red/green or good/bad reading
GROUP_COLOURS = {'A': '#0072B2', 'B': '#E69F00', 'C': '#CC79A7'}
