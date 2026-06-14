#!/usr/bin/env bash
# Bundle a phase for Kaggle submission.
set -euo pipefail
PHASE="${1:-phase3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/submission.tar.gz"

case "$PHASE" in
  phase0) FILES=(main.py) ;;
  phase1) FILES=(main.py geometry.py agent.py) ;;
  phase2|phase3) FILES=(main.py geometry.py simulation.py agent.py) ;;
  phase4) FILES=(main.py geometry.py simulation.py agent.py world_model.py asra_reasoner.py) ;;
  phase5) FILES=(main.py geometry.py simulation.py agent.py allocator.py) ;;
  phase6) FILES=(main.py geometry.py simulation.py agent.py allocator.py) ;;
  phase7) FILES=(main.py geometry.py simulation.py agent.py) ;;
  phase8) FILES=(main.py geometry.py simulation.py agent.py) ;;
  phase3-agg)
    PHASE_DIR="phase3"
    BUILD_DIR="$(mktemp -d)"
  trap 'rm -rf "$BUILD_DIR"' EXIT
    cp "${ROOT}/phase3"/{geometry.py,simulation.py,agent.py} "$BUILD_DIR/"
    cp "${ROOT}/phase3/variant_aggressive.py" "$BUILD_DIR/main.py"
    tar -czf "$OUT" -C "$BUILD_DIR" main.py geometry.py simulation.py agent.py
    echo "Created ${OUT} from phase3 aggressive variant"
    echo "Submit: kaggle competitions submit orbit-wars -f ${OUT} -m \"phase3 aggressive\""
    exit 0
    ;;
  *)
    echo "Unknown phase: $PHASE (use phase0–phase8, phase3-agg)"
    exit 1
    ;;
esac

PHASE_DIR="${PHASE_DIR:-$PHASE}"

# Only include files that exist
EXISTING=()
for f in "${FILES[@]}"; do
  [[ -f "${ROOT}/${PHASE_DIR}/${f}" ]] && EXISTING+=("$f")
done

tar -czf "$OUT" -C "${ROOT}/${PHASE_DIR}" "${EXISTING[@]}"
echo "Created ${OUT} from ${PHASE_DIR}/ (${EXISTING[*]})"
echo "Submit: kaggle competitions submit orbit-wars -f ${OUT} -m \"${PHASE} submit\""
