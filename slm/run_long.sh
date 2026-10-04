#!/usr/bin/env bash
# Run pipeline.py like an operator: on AC power, awake, logged, and resumed after a crash.
#
#   ./run_long.sh L-A --profile full
#   ./run_long.sh L-A L-B --profile full --allow-battery     # not recommended
#
# - Refuses to start on battery. Multi-hour runs drain it and macOS throttles on low power.
# - caffeinate -dims keeps the display, idle sleep, disk and system awake for the run.
# - Retries up to 5 times if training dies (the trainer resumes from its last checkpoint).
#   A deliberate Ctrl-C (exit 130) stops the loop.
# - Logs to runs/logs/<timestamp>.log, and samples thermal state every 10 minutes: a fanless
#   MacBook Air throttles hard over multi-day runs, a Mac mini or a MacBook Pro much less.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"

args=(); allow_battery=0
for a in "$@"; do
  if [[ "$a" == "--allow-battery" ]]; then allow_battery=1; else args+=("$a"); fi
done
if (( ! allow_battery )) && ! pmset -g batt | grep -q "AC Power"; then
  echo "not on AC power; plug in, or pass --allow-battery" >&2; exit 1
fi

mkdir -p runs/logs
log="runs/logs/$(date +%Y%m%d-%H%M%S).log"
echo "logging to $log"

( while sleep 600; do
    printf '%s thermal: %s\n' "$(date +%H:%M:%S)" "$(pmset -g therm 2>/dev/null | grep -Eo 'CPU_Speed_Limit[^,]*|No thermal warning level has been recorded' | head -1)"
  done ) >> "$log" 2>&1 &
monitor=$!
trap 'kill $monitor 2>/dev/null' EXIT

for attempt in 1 2 3 4 5; do
  caffeinate -dims uv run pipeline.py "${args[@]}" 2>&1 | tee -a "$log"
  rc=${PIPESTATUS[0]}
  if (( rc == 0 )); then echo "done" | tee -a "$log"; exit 0; fi
  if (( rc == 130 )); then echo "stopped by operator; re-run to resume" | tee -a "$log"; exit 130; fi
  echo "attempt $attempt exited $rc; resuming in 60 s" | tee -a "$log"
  sleep 60
done
echo "giving up after 5 attempts" | tee -a "$log"; exit 1
