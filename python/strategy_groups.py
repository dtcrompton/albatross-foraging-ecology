"""
Display names and colours for the three k-means foraging-strategy groups.

Shared by the Phase 3 figure and the Phase 4 map so their colours cannot drift
apart. The groups come from foraging-strategy metrics only and use no fishing data.
"""

# Legacy risk_label value -> group letter
GROUP_FROM_RISK_LABEL = {'Low risk': 'A', 'Medium risk': 'B', 'High risk': 'C'}

# Blue, dark amber and magenta-purple: colour-blind safe, no red/green or good/bad reading,
# and each at least 3:1 contrast against white (5.2, 4.0 and 6.1)
GROUP_COLOURS = {'A': '#0072B2', 'B': '#B86E00', 'C': '#AA3377'}
