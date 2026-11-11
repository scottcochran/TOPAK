# The bundle tier's entrypoint for this bundle. The mechanism evaluates `data.topak.bundle.allow`, and anything
# but an affirmative `true` is a deny (ADR-0030 §1). A bundle can only refuse.
package topak.bundle

import data.topak.standing

default allow := false

allow if not refused

refused if count(standing.violations) > 0

violations := standing.violations
