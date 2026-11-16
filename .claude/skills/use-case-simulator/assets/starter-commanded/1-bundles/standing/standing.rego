# A deployment's standing rules. Replace these. Start each reason with a stable identifier and a colon.
package topak.standing

known_tool if {
	some key
	data.topak.tools[key].name == input.resource.tool
}

violations contains "S1: the tool is not on the allowlist" if {
	input.action == "Actuate"
	not known_tool
}

violations contains "S2: only a person routes" if {
	input.action == "Route"
	input.principal.seat != "orc1"
}
