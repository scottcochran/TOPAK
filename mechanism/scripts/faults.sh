#!/usr/bin/env bash
# Crash and partition on the compose cluster (compose.cluster.yml), run from the host after
# `docker compose -f compose.cluster.yml up -d --build`.
#
#   1. Crash: kill the leader, order an entry through the two survivors, restart it with its log on
#      the volume, and watch it catch up, including the entry decided while it was down.
#   2. Partition: disconnect the leader from the network, try to order an entry through it (the
#      minority) and through the other two (the majority), reconnect it, and watch it converge.
#
# Every step asks the replicas through their operator sockets on the shared `dev` volume, from a
# client container, so a replica cut off from the network still answers `status`. One machine: this
# shows crash-recovery and a clean partition, not a slow disk, clock skew or a Byzantine replica.
set -euo pipefail
cd "$(dirname "$0")/.."
dc() { docker compose -f compose.cluster.yml "$@"; }
net="topak-cluster_default"

# Run a shell snippet in a client container on the dev volume.
in_client() { dc run --rm --no-deps -T client sh -c "$1"; }

status() {
  in_client 'for n in 1 2 3; do
    s="$(timeout 3 topak op --socket dev/run/n$n/operator.sock "{\"op\":\"status\"}" 2>/dev/null)" \
      && printf "  replica %s: %s\n" "$n" "$(echo "$s" | jq -c "{leader, last_applied, epoch}")" \
      || printf "  replica %s: no answer\n" "$n"
  done'
}

leader() {
  in_client 'for n in 1 2 3; do
    timeout 3 topak op --socket dev/run/n$n/operator.sock "{\"op\":\"status\"}" 2>/dev/null \
      | jq -e .leader >/dev/null && { echo $n; exit 0; }
  done; exit 1'
}

# fence_epoch through replica $1; prints the reply, or that none came within the timeout.
fence() {
  in_client "r=\$(timeout ${2:-5} topak op --socket dev/run/n$1/operator.sock \
    '{\"op\":\"fence_epoch\",\"reason\":\"faults\",\"attribution\":\"faults.sh\"}') \
    && echo \"\$r\" | jq -c '{slot, applied}' || echo '  (no reply in ${2:-5} s: not ordered)'"
}

# Wait until replica $1 answers and its last_applied equals the highest among the replicas.
caught_up() {
  for _ in $(seq 1 60); do
    if in_client "set -e; a=\$(timeout 3 topak op --socket dev/run/n$1/operator.sock '{\"op\":\"status\"}' | jq .last_applied)
      m=0; for n in 1 2 3; do v=\$(timeout 3 topak op --socket dev/run/n\$n/operator.sock '{\"op\":\"status\"}' 2>/dev/null | jq .last_applied) || v=0
      [ \"\$v\" -gt \"\$m\" ] && m=\$v; done; [ \"\$a\" -eq \"\$m\" ]" >/dev/null 2>&1; then return 0; fi
    sleep 1
  done
  echo "replica $1 did not catch up in 60 s" >&2; return 1
}

others() { for n in 1 2 3; do [ "$n" != "$1" ] && echo "$n"; done; }

echo "== before"; status
L="$(leader)"; set -- $(others "$L"); A="$1"; B="$2"
echo "leader is replica $L"

echo; echo "== 1. crash: kill replica $L (the leader)"
dc kill "n$L" >/dev/null
echo "fence_epoch through replica $A, with $L down:"; fence "$A" 10
status
echo "restart replica $L"
# Plain docker, not `docker compose start`, which would also start the replica's dependencies again.
docker start "topak-cluster-n$L-1" >/dev/null
caught_up "$L"
echo "replica $L is back and has caught up:"; status

L="$(leader)"; set -- $(others "$L"); A="$1"; B="$2"
echo; echo "== 2. partition: disconnect replica $L (the leader) from the network"
docker network disconnect "$net" "topak-cluster-n$L-1"
echo "fence_epoch through replica $L (the minority):"; fence "$L" 5
echo "fence_epoch through replica $A (the majority):"; fence "$A" 10
echo "(replica $L may still report leader=true: it cannot reach a majority, so it orders nothing)"
status
echo "reconnect replica $L"
docker network connect --alias "n$L" "$net" "topak-cluster-n$L-1"
caught_up "$L"
echo "replica $L converged:"; status

echo; echo "== round topics in Kafka"
dc exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list | sed 's/^/  /'
