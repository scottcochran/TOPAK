//! Trace recording for refinement checking against `spec/Mechanism.tla` (ADR-0045 T-0045-28,
//! stage 1: trace validation).
//!
//! When a `State` carries a trace name and `TOPAK_TRACE_DIR` is set, every `apply` appends one
//! JSON line to `<dir>/<name>.jsonl`: the log index, the entry, the result, and a **projection**
//! of the state after it. The first line of a file is the projection before the first entry.
//! `spec/trace2tla.py` turns the file into a TLA+ constant and TLC checks that the operational
//! module reproduces every step: same projected state, same result kind.
//!
//! The projection is the state the module models, in the shapes the module's header fixes.
//! What is *not* modelled is carried as an **oracle** on the entry: whether an issuance passed
//! `validate_issuance` (signatures and the rules floor), whether a break-glass approval's
//! signature verified, and whether an admit's parameter digest matched; and, for confinement
//! (ADR-0034), whether an appraisal's signature verified and under which key, whether a session
//! proof verified under the lease's key, and what a registered profile file parses to; for an
//! operator (ADR-0050), whether a request's signature is its seat's, whether a sign-on assertion
//! verifies, and which seat a revocation was lifted on; for an activation (ADR-0052), which
//! roster keys approved it. Those are the trace's trusted inputs, and the module says so.
//!
//! JSON encoding: `{"$f": [[k, v], ...]}` is a TLA+ function, `{"$s": [...]}` a set, an array a
//! tuple, any other object a record. A round topic is the tuple `<<seat, epoch, round>>`.

use serde_json::{Value, json};
use std::io::Write;
use std::sync::atomic::{AtomicU64, Ordering};

use crate::authentic::{self, Signed};
use crate::confine::*;
use crate::control::*;
use crate::labels::{Delivery, ItemLabel, LabelFacts};
use crate::rules::{self, Quorum, Rules};
use crate::state::*;
use crate::types::*;

pub const ENV_DIR: &str = "TOPAK_TRACE_DIR";

static COUNTER: AtomicU64 = AtomicU64::new(0);

/// A trace name for a state built in a test, when tracing is on: the test thread's name plus a
/// per-process counter, so two states in one test do not share a file.
pub fn name_from_env(prefix: &str) -> Option<String> {
    std::env::var(ENV_DIR).ok()?;
    let thread = std::thread::current().name().unwrap_or("trace").replace("::", "-");
    let n = COUNTER.fetch_add(1, Ordering::SeqCst);
    Some(format!("{prefix}-{thread}-{n}"))
}

pub fn enabled(state: &State) -> bool {
    state.trace.is_some() && std::env::var(ENV_DIR).is_ok()
}

/// Whether an appraisal's signature verifies, and the key it names. The model checks the key is
/// an issued verifier key; the cryptography is the trace's.
fn sig_oracle(a: &Appraisal) -> Value {
    let ok = a.signature.as_ref().is_some_and(|s| authentic::verify(APPRAISAL_PURPOSE, &a.body(), s));
    json!({ "sigOk": ok, "sigKey": none_or(a.signature.as_ref().map(|s| s.key.clone())) })
}

/// The facts the module takes from the trace rather than computing (see the module header).
pub fn oracle(state: &State, entry: &Entry, params: &Params) -> Value {
    match entry {
        Entry::Grant { appraisal: Some(a), .. }
        | Entry::Renew { appraisal: Some(a), .. }
        | Entry::Contested { appraisal: a, .. } => sig_oracle(a),
        Entry::ProfileRegister { profile, .. } => {
            let parsed = Profile::parse(profile);
            let ok = parsed.as_ref().is_ok_and(|p| p.check_well_formed().is_empty());
            json!({
                "ok": ok,
                "digest": Digest::of(profile.as_bytes()).0,
                "artifact": profile_artifact(profile.as_bytes()).0,
                "profile": parsed.as_ref().map(project_profile).unwrap_or_else(|_| json!("none")),
            })
        }
        Entry::Grant { req, .. } => json!({ "signOnOk": grant_sign_on(state, req) }),
        Entry::Control { control, grant, .. } => {
            let req = &control.request;
            let decl = state.rules.seats.get(&req.operator);
            let sig_ok = decl.is_some_and(|d| d.key == control.sig.key)
                && authentic::verify(CONTROL_PURPOSE, &req.body(&state.chain), &control.sig);
            let last = |seat: &str| state.last_lease.get(seat).copied().unwrap_or(0);
            let fresh = decl.is_some_and(|d| {
                let (p, a) = (&state.rules.provider_keys, control.assertion.as_ref());
                sign_on_verifies(p, &state.chain, &d.key, state.epoch, last(&req.operator), a)
            });
            // The sign-on a Regrant or a Renew carries for a target that is an operator.
            let (target, sign_on) = match &req.action {
                ControlAction::Regrant { target, sign_on, .. } | ControlAction::Renew { target, sign_on, .. } => {
                    (Some(target), sign_on.as_ref())
                }
                _ => (None, None),
            };
            let target_ok = target.and_then(|t| state.rules.seats.get(t).map(|d| (t, d))).is_some_and(|(t, d)| {
                sign_on_verifies(&state.rules.provider_keys, &state.chain, &d.key, state.epoch, last(t), sign_on)
            });
            let same = grant.as_ref().is_none_or(|g| g.sign_on.as_ref() == sign_on);
            json!({ "sigOk": sig_ok, "freshOk": fresh, "targetSignOnOk": target_ok, "signOnSame": same })
        }
        Entry::Activate { activation, approvals, .. } => {
            let body = activation.body(&state.chain);
            let roster = state.rules.break_glass.as_ref().map(|bg| &bg.roster);
            let ok = |s: &&Signed| {
                roster.is_some_and(|r| r.contains(&s.key)) && authentic::verify(ACTIVATION_PURPOSE, &body, s)
            };
            json!({ "approvers": setv(approvals.iter().filter(ok).map(|s| s.key.clone()).collect::<std::collections::BTreeSet<_>>()) })
        }
        Entry::Admit { rec, .. } if rec.session.is_some() => {
            let proof = rec.session.as_ref().expect("checked");
            let lease = state.leases.get(&rec.lease);
            let key = lease
                .and_then(|l| l.attestation.as_ref())
                .and_then(|a| a.session_key.clone())
                .or_else(|| lease.and_then(|l| l.person.clone()));
            let body = session_body(rec.lease, rec.epoch, proof.ctr, &proof.op);
            let proof_ok = key.is_some_and(|k| {
                authentic::verify(AGENT_OP_PURPOSE, &body, &Signed { key: k, sig: proof.sig.clone() })
            });
            json!({ "ok": rec.params == params.digest(), "proofOk": proof_ok })
        }
        Entry::Issue { issuance, .. } => {
            json!({ "ok": rules::validate_issuance(&state.rules, issuance, state.floor_exceptions).is_ok() })
        }
        Entry::BreakGlassApprove { seat, epoch, approval, .. } => {
            let body = json!({ "seat": seat, "epoch": epoch });
            json!({ "ok": authentic::verify(BREAK_GLASS_PURPOSE, &body, approval) })
        }
        Entry::Admit { rec, .. } => json!({ "ok": rec.params == params.digest() }),
        _ => json!({}),
    }
}

pub fn record(
    pre: &State,
    post: &State,
    index: LogIndex,
    entry: &Entry,
    applied: &Applied,
    oracle: Value,
    params: &Params,
) {
    let (Some(name), Ok(dir)) = (post.trace.as_ref(), std::env::var(ENV_DIR)) else { return };
    let path = std::path::Path::new(&dir).join(format!("{name}.jsonl"));
    let fresh = !path.exists();
    let _ = std::fs::create_dir_all(&dir);
    let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(&path) else { return };
    if fresh {
        let _ = writeln!(f, "{}", json!({ "init": project_state(pre, params) }));
    }
    let line = json!({
        "index": index,
        "entry": project_entry(entry, oracle),
        "applied": project_applied(applied),
        "state": project_state(post, params),
    });
    let _ = writeln!(f, "{line}");
}

/// Whether a grant's sign-on assertion verifies for its seat at this state (ADR-0050 §3).
fn grant_sign_on(state: &State, req: &GrantRequest) -> bool {
    state.rules.seats.get(&req.seat).is_some_and(|d| {
        let last = state.last_lease.get(&req.seat).copied().unwrap_or(0);
        sign_on_verifies(&state.rules.provider_keys, &state.chain, &d.key, state.epoch, last, req.sign_on.as_ref())
    })
}

fn project_item(i: &ItemLabel) -> Value {
    json!({ "label": setv(i.label.iter().cloned()), "delivery": delivery(i.delivery) })
}

fn delivery(d: Delivery) -> &'static str {
    match d {
        Delivery::Clear => "clear",
        Delivery::Handle => "handle",
    }
}

fn project_labels(f: &LabelFacts) -> Value {
    json!({
        "clearSet": setv(f.clear_set.iter().cloned()), "resultLabel": setv(f.result_label.iter().cloned()),
        "delivery": delivery(f.delivery),
    })
}

/// A grant as the model reads it, on either path: the unsigned one, and inside a `Regrant`.
fn project_grant(req: &GrantRequest, sign_on_ok: bool) -> Value {
    json!({
        "principal": req.principal, "seat": req.seat, "persona": req.persona.0, "bundle": req.bundle.0,
        "conf": req.confinement.digest.0, "rung": req.confinement.rung,
        "alphabet": setv(req.alphabet.iter().map(|k| k.as_str())), "ttl": req.ttl_ms,
        "round": req.round, "role": req.role.as_str(),
        "taskLabelled": req.task_label.is_some(),
        "taskLabel": setv(req.task_label.iter().flatten().cloned()),
        "taskLabelsAllowed": setv(req.task_labels_allowed.iter().flatten().cloned()),
        "signOnOk": sign_on_ok,
    })
}

fn project_control_action(a: &ControlAction) -> Value {
    let names = |a: &std::collections::BTreeSet<ActionKind>| setv(a.iter().map(|k| k.as_str()));
    match a {
        ControlAction::Regrant { target, round, alphabet, ttl_ms, task_label, .. } => json!({
            "kind": "Regrant", "target": target, "round": round, "alphabet": names(alphabet), "ttl": ttl_ms,
            "taskLabelled": task_label.is_some(), "taskLabel": setv(task_label.iter().flatten().cloned()),
        }),
        ControlAction::Renew { target, alphabet, ttl_ms, .. } => {
            json!({ "kind": "Renew", "target": target, "alphabet": names(alphabet), "ttl": ttl_ms })
        }
        ControlAction::AttestGates { artifact, evidence } => {
            json!({ "kind": "AttestGates", "artifact": artifact.0, "evidence": evidence.0 })
        }
        ControlAction::EndRound { target } => json!({ "kind": "EndRound", "target": target }),
        ControlAction::Revoke { target, .. } => {
            json!({ "kind": "Revoke", "target": serde_json::to_value(target).unwrap() })
        }
        ControlAction::FenceEpoch { .. } => json!({ "kind": "FenceEpoch" }),
    }
}

fn project_facts(f: &ControlFacts) -> Value {
    json!({
        "personaInForce": f.persona_in_force, "hasLease": f.has_lease, "peerLive": f.peer_live,
        "freshAssertion": f.fresh_assertion, "targetSeated": f.target_seated, "targetLive": f.target_live,
        "sameBinding": f.same_binding, "nextRound": f.next_round,
        "lastAlphabet": setv(f.last_alphabet.iter().cloned()), "newAlphabet": setv(f.new_alphabet.iter().cloned()),
        "taskLabelled": f.task_labelled, "taskLabel": setv(f.task_label.iter().cloned()),
        "taskLabelsAllowed": setv(f.task_labels_allowed.iter().cloned()),
        "domain": none_or(f.domain.map(Domain::as_str)), "targetDomain": none_or(f.target_domain.map(Domain::as_str)),
        "targetSeat": none_or(f.target_seat.clone()),
    })
}

fn fnv<K: Into<Value>, V: Into<Value>>(pairs: impl IntoIterator<Item = (K, V)>) -> Value {
    json!({ "$f": pairs.into_iter().map(|(k, v)| json!([k.into(), v.into()])).collect::<Vec<_>>() })
}

fn setv<V: Into<Value>>(items: impl IntoIterator<Item = V>) -> Value {
    json!({ "$s": items.into_iter().map(Into::into).collect::<Vec<_>>() })
}

fn none_or<T: Into<Value>>(v: Option<T>) -> Value {
    v.map(Into::into).unwrap_or_else(|| json!("none"))
}

/// `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>` → `<<seat, epoch, round>>`.
pub fn topic_tuple(topic: &str) -> Value {
    let parts: Vec<&str> = topic.split('.').collect();
    let n = parts.len();
    if n >= 3
        && let (Some(e), Some(r)) = (parts[n - 2].strip_prefix('e'), parts[n - 1].strip_prefix('r'))
        && let (Ok(e), Ok(r)) = (e.parse::<u64>(), r.parse::<u64>())
    {
        return json!([parts[n - 3], e, r]);
    }
    json!([topic, 0, 0])
}

fn project_rules(r: &Rules) -> Value {
    json!({
        "rulesEpoch": r.rules_epoch,
        "seats": fnv(r.seats.iter().map(|(id, d)| (id.clone(), json!({
            "domain": d.domain.as_str(), "kind": d.kind.as_str(), "cell": none_or(d.cell.clone()), "rung": d.rung,
        })))),
        "grantRoster": setv(r.grant_roster.iter().cloned()),
        "vetoRoster": setv(r.veto_roster.iter().cloned()),
        "quorum": match r.quorum { Quorum::All => json!("all"), Quorum::Threshold(k) => json!(k) },
        "minGrant": r.min_grant,
        "bgIssued": r.break_glass.is_some(),
        "bgQuorum": r.break_glass.as_ref().map_or(0, |bg| bg.quorum),
        "bgRoster": setv(r.break_glass.iter().flat_map(|bg| bg.roster.iter().cloned())),
        "verifierKeys": setv(r.verifier_keys.iter().cloned()),
        "bundleKeys": setv(r.bundle_keys.iter().cloned()),
        "personas": fnv(r.personas.iter().map(|(d, p)| (d.0.clone(), p.as_str()))),
        "criterion": r.criterion.is_some(),
    })
}

/// A registered profile, as far as the model reads it: what P7 names and P3–P5's verdicts.
fn project_profile(p: &Profile) -> Value {
    let verdict = |c| p.verdict(c).map_or("none", ClauseVerdict::as_str);
    json!({
        "image": p.image.is_some(),
        "persona": none_or(p.persona.model_json_sha256.as_ref().map(|d| d.0.clone())),
        "measurement": none_or(p.reference.launch_measurement.clone()),
        "minTcb": none_or(p.reference.min_tcb), "domain": p.domain.as_str(),
        "p3": verdict(Clause::P3), "p4": verdict(Clause::P4), "p5": verdict(Clause::P5),
    })
}

fn project_appraisal(a: &Appraisal) -> Value {
    let st = &a.statement;
    json!({
        "verdict": st.verdict.as_str(), "rung": st.rung, "profile": st.profile.0, "persona": st.persona.0,
        "nEpoch": st.nonce.epoch, "nIndex": st.nonce.index, "principal": st.nonce.principal,
        "round": st.nonce.round, "key": none_or(st.session_key.clone()),
        "measurement": none_or(st.measurement.clone()), "tcb": none_or(st.tcb), "platform": st.platform,
        "gen": a.instance.0, "evidence": st.evidence.0,
    })
}

fn project_attestation(a: &Attestation) -> Value {
    json!({
        "verdict": a.verdict.as_str(), "nEpoch": a.n_epoch, "nIndex": a.nonce_index, "gen": a.instance.0,
        "key": none_or(a.session_key.clone()), "platform": a.platform,
    })
}

pub fn project_state(s: &State, params: &Params) -> Value {
    let r = project_rules(&s.rules);
    let lease = |lr: &LeaseRecord| {
        let l = &lr.lease;
        json!({
            "principal": l.principal, "seat": l.seat, "persona": l.persona.0, "bundle": l.bundle.0,
            "epoch": l.epoch, "rulesEpoch": l.rules_epoch, "conf": l.confinement.digest.0,
            "rung": l.confinement.rung, "alphabet": setv(l.alphabet.iter().map(|k| k.as_str())),
            "round": l.round, "role": l.role.as_str(), "ttl": l.ttl_ms,
            "ended": none_or(lr.ended.map(|e| serde_json::to_value(e).unwrap())),
            "actions": lr.actions, "seq": lr.seq,
            "att": lr.attestation.as_ref().map_or_else(|| json!("none"), project_attestation),
            "sessionCtr": lr.session_ctr,
            "clearSet": setv(lr.labels.clear_set.iter().cloned()),
            "results": fnv(lr.labels.results.iter().map(|(seq, i)| (*seq, project_item(i)))),
            "consults": fnv(lr.labels.consults.iter().map(|(d, i)| (d.0.clone(), project_item(i)))),
            "person": none_or(lr.person.clone()),
            "envelope": fnv(lr.envelope.iter().flatten().map(|(t, rev)| (t.clone(), rev.0.clone()))),
        })
    };
    let mut v = json!({
        "epoch": s.epoch,
        "rulesEpoch": r["rulesEpoch"], "seats": r["seats"], "grantRoster": r["grantRoster"],
        "vetoRoster": r["vetoRoster"], "quorum": r["quorum"], "minGrant": r["minGrant"],
        "bgIssued": r["bgIssued"], "bgRoster": r["bgRoster"], "bgQuorum": r["bgQuorum"],
        "verifierKeys": r["verifierKeys"], "bundleKeys": r["bundleKeys"],
        "personas": r["personas"], "criterion": r["criterion"],
        "tPersona": s.persona.t_persona_ms,
        "leases": fnv(s.leases.iter().map(|(f, lr)| (*f, lease(lr)))),
        "liveBySeat": fnv(s.live_by_seat.iter().map(|(k, v)| (k.clone(), *v))),
        "lastRound": fnv(s.last_round.iter().map(|(k, v)| (k.clone(), *v))),
        "candidates": fnv(s.candidates.iter().map(|(a, c)| (a.0.clone(), json!({
            "artifact": c.artifact.0, "author": c.author,
            "votes": fnv(c.votes.iter().map(|(seat, v)| (seat.clone(), json!({
                "verdict": v.verdict.as_str(), "evidence": v.evidence.0, "rulesEpoch": v.rules_epoch,
            })))),
            "promotedAt": none_or(c.promoted_at),
        })))),
        "gates": fnv(s.gates.iter().map(|(a, e)| (a.0.clone(), e.0.clone()))),
        "approvals": fnv(s.break_glass.iter().map(|(seat, by_epoch)| (seat.clone(),
            fnv(by_epoch.iter().map(|(ep, keys)| (*ep, setv(keys.iter().cloned()))))))),
        "revoked": setv(s.revoked.iter().map(|t| serde_json::to_value(t).unwrap())),
        "appliedIds": setv(s.applied_ids.iter().cloned()),
        "lastApplied": s.last_applied,
        "k": s.observer.k,
        "marks": fnv(s.marks.iter().map(|(o, m)| (o.clone(),
            fnv(m.iter().map(|(topic, wm)| (topic_tuple(topic), *wm)))))),
        "seals": fnv(s.seals.iter().map(|(seat, sl)| (seat.clone(), json!({ "topic": topic_tuple(&sl.topic), "seq": sl.seq })))),
        "profiles": fnv(s.profiles.iter().map(|(d, pr)| (d.0.clone(), json!({
            "artifact": pr.artifact.0, "summary": project_profile(&pr.profile), "registeredAt": pr.registered_at,
        })))),
        "contested": fnv(s.contested.iter().map(|(p, e)| (p.clone(), e.0.clone()))),
        "contained": setv(s.leases.keys().filter(|f| s.contained(**f).contained).copied()),
        "wasmTools": setv(params.wasm_tools.iter().cloned()),
        "buildBound": params.round_bound_for(Domain::Build),
        "runBound": params.round_bound_for(Domain::Run),
    });
    // ADR-0050 and ADR-0052. Set after the literal, which is as deep as the macro goes.
    v["seatings"] = fnv(s.seatings.iter().map(|(seat, g)| (seat.clone(), json!({
            "principal": g.principal, "persona": g.persona.0, "bundle": g.bundle.0,
            "conf": g.confinement.digest.0, "rung": g.confinement.rung,
            "alphabet": setv(g.alphabet.iter().map(|k| k.as_str())), "role": g.role.as_str(),
            "taskLabels": setv(g.task_labels.iter().cloned()),
        }))));
    v["lastLease"] = fnv(s.last_lease.iter().map(|(k, v)| (k.clone(), *v)));
    v["controlCtr"] = fnv(s.control_ctr.iter().map(|(k, v)| (k.clone(), *v)));
    v["emSeatings"] = fnv(s.emergency_seatings.iter().map(|(seat, g)| (seat.clone(), project_em_seating(g))));
    v["activations"] = Value::Array(s.activations.iter().map(|a| json!({
            "at": a.at, "seat": a.activation.seat, "person": a.activation.person, "epoch": a.activation.epoch,
            "round": a.activation.round, "approvers": setv(a.approvers.iter().cloned()), "drill": a.drill,
        })).collect());
    v
}

fn project_em_seating(g: &EmergencySeating) -> Value {
    let (domain, named) = match &g.envelope {
        Envelope::Domain => (true, setv(Vec::<String>::new())),
        Envelope::Named(n) => (false, setv(n.iter().cloned())),
    };
    json!({
        "persons": setv(g.persons.iter().cloned()), "bundle": g.bundle.0, "envDomain": domain, "envNamed": named,
        "taskLabels": setv(g.task_labels.iter().cloned()), "drill": g.drill,
    })
}

fn project_action(a: &Admitted) -> Value {
    match a {
        Admitted::Consult { object } => json!({ "kind": "Consult", "object": object.0 }),
        Admitted::Submit { artifact } => json!({ "kind": "Submit", "artifact": artifact.0 }),
        Admitted::Vote { verdict, artifact, evidence, rules_epoch } => json!({
            "kind": "Vote", "verdict": verdict.as_str(), "artifact": artifact.0,
            "evidence": evidence.0, "rulesEpoch": rules_epoch,
        }),
        Admitted::Actuate { tool, .. } => json!({ "kind": "Actuate", "tool": tool }),
        Admitted::Heartbeat { via, topic, watermark } => json!({
            "kind": "Heartbeat", "via": via.as_str(), "topic": topic_tuple(topic), "watermark": watermark,
        }),
        other => json!({ "kind": other.kind().as_str() }),
    }
}

pub fn project_entry(e: &Entry, oracle: Value) -> Value {
    let mut v = match e {
        Entry::Grant { id, req, appraisal } => {
            let mut g = project_grant(req, false);
            g["kind"] = json!("Grant");
            g["id"] = json!(id);
            g["appraisal"] = appraisal.as_ref().map_or_else(|| json!("none"), project_appraisal);
            g["sigOk"] = json!(false);
            g["sigKey"] = json!("none");
            g
        }
        Entry::Renew { id, req, appraisal } => json!({
            "kind": "Renew", "id": id, "seat": req.seat, "fence": req.fence,
            "alphabet": setv(req.alphabet.iter().map(|k| k.as_str())), "rung": req.rung, "ttl": req.ttl_ms,
            "appraisal": appraisal.as_ref().map_or_else(|| json!("none"), project_appraisal),
            "sigOk": false, "sigKey": "none",
        }),
        Entry::Admit { id, rec } => json!({
            "kind": "Admit", "id": id, "seat": rec.seat, "lease": rec.lease, "epoch": rec.epoch,
            "action": project_action(&rec.action),
            "session": rec.session.as_ref().map_or_else(|| json!("none"), |p| json!({ "ctr": p.ctr })),
            "proofOk": false,
            "labels": rec.labels.as_ref().map_or_else(|| json!("none"), project_labels),
        }),
        Entry::Contested { id, appraisal, .. } => json!({
            "kind": "Contested", "id": id, "appraisal": project_appraisal(appraisal),
        }),
        Entry::ProfileRegister { id, .. } => json!({ "kind": "ProfileRegister", "id": id }),
        Entry::EndRound { id, seat, fence, reason, .. } => json!({
            "kind": "EndRound", "id": id, "seat": seat, "fence": fence, "reason": serde_json::to_value(reason).unwrap(),
        }),
        Entry::Revoke { id, target, .. } => {
            json!({ "kind": "Revoke", "id": id, "target": serde_json::to_value(target).unwrap() })
        }
        Entry::EpochIncrement { id, .. } => json!({ "kind": "EpochIncrement", "id": id }),
        Entry::EmergencySeating { id, seat, seating } => {
            json!({ "kind": "EmergencySeating", "id": id, "seat": seat, "seating": project_em_seating(seating) })
        }
        // The grant an activation makes names the person as its principal, a Persona that is the
        // digest of the key, and no confinement: projected here so the model builds the same lease.
        Entry::Activate { id, activation: a, envelope, .. } => json!({
            "kind": "Activate", "id": id, "seat": a.seat, "person": a.person, "epoch": a.epoch,
            "round": a.round, "ttl": a.ttl_ms, "taskSome": a.task.is_some(),
            "taskLabelled": a.task_label.is_some(), "taskLabel": setv(a.task_label.iter().flatten().cloned()),
            "persona": Digest::of(a.person.as_bytes()).0, "conf": Digest::of(b"none").0,
            "envelope": fnv(envelope.iter().map(|(t, rev)| (t.clone(), rev.0.clone()))),
        }),
        // A `Regrant`'s grant and a `Renew`'s renewal are projected as the unsigned entries are,
        // so the model applies them with the same operators. A control entry carries no
        // appraisal at the reference: a successor at rung 1 or above is not built.
        Entry::Control { id, control, grant, renew, .. } => {
            let sign_on_ok = oracle["targetSignOnOk"].as_bool().unwrap_or(false);
            let renew = renew.as_ref().map(|r| json!({
                "seat": r.seat, "fence": r.fence, "alphabet": setv(r.alphabet.iter().map(|k| k.as_str())),
                "rung": r.rung, "ttl": r.ttl_ms, "appraisal": "none", "sigOk": false, "sigKey": "none",
            }));
            let grant = grant.as_ref().map(|g| {
                let mut g = project_grant(g, sign_on_ok);
                g["appraisal"] = json!("none");
                g["sigOk"] = json!(false);
                g["sigKey"] = json!("none");
                g
            });
            json!({
                "kind": "Control", "id": id, "operator": control.request.operator,
                "epoch": control.request.epoch, "ctr": control.request.ctr,
                "action": project_control_action(&control.request.action),
                "facts": project_facts(&control.facts),
                "grant": none_or(grant), "renew": none_or(renew),
            })
        }
        Entry::Issue { id, issuance } => json!({ "kind": "Issue", "id": id, "rules": project_rules(&issuance.rules) }),
        Entry::GatesPassed { id, artifact, evidence } => json!({
            "kind": "GatesPassed", "id": id, "artifact": artifact.0, "evidence": evidence.0,
        }),
        Entry::BreakGlassApprove { id, seat, epoch, approval } => json!({
            "kind": "BreakGlassApprove", "id": id, "seat": seat, "epoch": epoch, "key": approval.key,
        }),
    };
    if let (Some(obj), Some(o)) = (v.as_object_mut(), oracle.as_object()) {
        for (k, val) in o {
            obj.insert(k.clone(), val.clone());
        }
    }
    v
}

pub fn project_applied(a: &Applied) -> Value {
    match a {
        Applied::EmergencyPrepared => json!({ "kind": "EmergencyPrepared" }),
        Applied::LeaseGranted { fence } => json!({ "kind": "LeaseGranted", "fence": fence }),
        Applied::Renewed { fence } => json!({ "kind": "Renewed", "fence": fence }),
        Applied::Admitted { seq, promoted } => json!({
            "kind": "Admitted", "seq": none_or(*seq), "promoted": none_or(promoted.as_ref().map(|d| d.0.clone())),
        }),
        Applied::RoundEnded => json!({ "kind": "RoundEnded" }),
        Applied::Revoked { ended } => json!({ "kind": "Revoked", "ended": ended }),
        Applied::EpochIncremented { epoch } => json!({ "kind": "EpochIncremented", "epoch": epoch }),
        Applied::Contested { ended } => json!({ "kind": "Contested", "ended": ended }),
        Applied::ProfileRegistered { digest } => json!({ "kind": "ProfileRegistered", "digest": digest.0 }),
        Applied::Issued { rules_epoch } => json!({ "kind": "Issued", "rulesEpoch": rules_epoch }),
        Applied::GatesRecorded => json!({ "kind": "GatesRecorded" }),
        Applied::BreakGlassApproved { approvals } => json!({ "kind": "BreakGlassApproved", "approvals": approvals }),
        Applied::Rejected(_) => json!({ "kind": "Rejected" }),
        Applied::Duplicate => json!({ "kind": "Duplicate" }),
    }
}
