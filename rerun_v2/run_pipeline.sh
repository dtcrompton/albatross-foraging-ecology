#!/bin/sh
# Usage, from the repository root: sh rerun_v2/run_pipeline.sh control|v2|v3
set -e
RUN=$1
case $RUN in
  control) PROC=data/processed_v2/control; OUT=outputs_v2/control ;;
  v2)      PROC=data/processed_v2;         OUT=outputs_v2 ;;
  v3)      PROC=data/processed_v3;         OUT=outputs_v2/v3 ;;
  *) echo "unknown run $RUN"; exit 2 ;;
esac
mkdir -p "$PROC" "$OUT/figures" rerun_v2/logs
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1
for s in phase1_movement_metrics phase2a_behaviour_classification \
         phase2b_environmental_drivers phase3_conservation_risk; do
  echo "== $RUN $s $(date)"
  python3 "rerun_v2/$RUN/$s.py" > "rerun_v2/logs/${RUN}_$s.log" 2>&1
done
if [ "$RUN" != control ]; then python3 rerun_v2/strip_audit_columns.py "$PROC"; fi
echo "== $RUN finished $(date)"
