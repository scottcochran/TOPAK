#!/usr/bin/env bash
# Generate a three-replica dev environment under mechanism/dev/.
#
#   scripts/dev-init.sh            # in-memory transport, local WASM bundle only
#   scripts/dev-init.sh --kafka    # Kafka at 127.0.0.1:9092 (docker compose up kafka)
#   scripts/dev-init.sh --opa      # OPA sidecar at 127.0.0.1:8181 (docker compose up opa; host port 18181)
#
# DEV RULES, NOT GENESIS RULES. Keys are generated here and their secrets are written to
# dev/secrets/ in the clear. Nothing produced by this script is a genesis bundle.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
dev="$here/dev"
kafka=null; opa=null
for a in "$@"; do
  case "$a" in
    --kafka) kafka='{"brokers":["127.0.0.1:9092"],"replication":1}' ;;
    --opa) opa='"http://127.0.0.1:18181"' ;;
  esac
done

cargo build -q --manifest-path "$here/Cargo.toml" -p topak-node
bin="$here/target/debug"
rev="$("$here/scripts/build-bundle.sh" 2>/dev/null)"

rm -rf "$dev"; mkdir -p "$dev/corpus" "$dev/secrets" "$dev/run" "$dev/bundles"
echo "TOPAK_BUNDLE=$rev" > "$here/.env"

# Corpus: the repository's TLA+ modules, content-addressed.
for f in "$here"/../spec/*.tla; do
  d="$(shasum -a 256 "$f" | cut -d' ' -f1)"; cp "$f" "$dev/corpus/$d"
done
corpus="$(ls "$dev/corpus" | jq -R . | jq -s .)"

# The demo tool's allowlist id pins its binary and its MCP schema.
td="$("$bin/topak" tool-digest --command "$bin/topak-demo-tool" --tool wordcount 2>/dev/null)"
tool_id="$(jq -r .id <<<"$td")"; tool_bin="$(jq -r .binary_sha256 <<<"$td")"

key() { "$bin/topak" keygen > "$dev/secrets/$1.json"; jq -r .public "$dev/secrets/$1.json"; }
for s in a1 g1 g2 g3 o1 corr r1 ro1; do declare "seat_$s=$(key "seat-$s")"; done
anchors="$(for i in 1 2 3; do key "anchor-$i"; done | jq -R . | jq -s .)"
bgk="$(for i in 1 2; do key "bg-$i"; done | jq -R . | jq -s .)"
# ADR-0044: the dev bundle key signs a copy of the built bundle into dev/bundles/; the rules carry
# its public key under bundle_keys (ADR-0025 §1 (f)). The tracked tarball in bundles/ stays unsigned.
bundle_pub="$(key bundle)"
cp "$here/bundles/$rev.tar.gz" "$dev/bundles/"
"$bin/topak" sign --purpose bundle --secret "$(jq -r .secret "$dev/secrets/bundle.json")" \
  <(printf '{"revision":"%s"}' "$rev") > "$dev/bundles/$rev.sig"

jq -n --argjson anchors "$anchors" --argjson bg "$bgk" --arg tool "$tool_id" --arg bundle_pub "$bundle_pub" \
  --arg a1 "$seat_a1" --arg g1 "$seat_g1" --arg g2 "$seat_g2" --arg g3 "$seat_g3" --arg o1 "$seat_o1" --arg corr "$seat_corr" --arg r1 "$seat_r1" --arg ro1 "$seat_ro1" '{
  rules_epoch: 0, quorum: "all", min_grant: 2,
  seats: {
    a1: {domain: "build", kind: "thinker", key: $a1}, g1: {domain: "build", kind: "grant", key: $g1},
    g2: {domain: "build", kind: "grant", key: $g2}, g3: {domain: "build", kind: "grant", key: $g3},
    o1: {domain: "build", kind: "observer", cell: "a1", key: $o1},
    corr: {domain: "build", kind: "observer", key: $corr},
    r1: {domain: "run", kind: "thinker", key: $r1},
    ro1: {domain: "run", kind: "observer", cell: "r1", key: $ro1}
  },
  grant_roster: ["g1", "g2", "g3"], veto_roster: ["o1", "corr"],
  anchor_keys: $anchors,
  break_glass: {roster: $bg, quorum: 2, tools: [$tool], actions: ["Actuate"]},
  erasure_roster: null,
  verifier_keys: [], bundle_keys: [$bundle_pub]
}' > "$dev/rules.json"

jq -n --argjson corpus "$corpus" --arg tool "$tool_id" '{
  corpus: $corpus, build_tools: [$tool], run_tools: [], run_root: [], round_bound: 200, run_round_bound: 64,
  lease_margin_ms: 500,
  after_topic_limit: 64
}' > "$dev/params.json"

for i in 1 2 3; do
  jq -n --argjson id "$i" --argjson kafka "$kafka" --argjson opa "$opa" \
    --arg tool "$tool_id" --arg cmd "$bin/topak-demo-tool" --arg bin_sha "$tool_bin" '{
    id: $id,
    peers: {"1": "127.0.0.1:7101", "2": "127.0.0.1:7102", "3": "127.0.0.1:7103"},
    data_dir: "run/n\($id)", agent_socket: "run/n\($id)/agent.sock", operator_socket: "run/n\($id)/operator.sock",
    rules: "rules.json", params: "params.json", corpus_dir: "corpus", bundles_dir: "bundles",
    opa_sidecar: $opa, kafka: $kafka,
    tools: {($tool): {command: $cmd, args: [], binary_sha256: $bin_sha, mcp_tool: "wordcount"}}
  }' > "$dev/n$i.json"
done

"$bin/topak" check-rules "$dev/rules.json"
echo "bundle   $rev  (signed copy in dev/bundles/, key dev/secrets/bundle.json)"
echo "tool     $tool_id"
echo "configs  $dev/n{1,2,3}.json"
