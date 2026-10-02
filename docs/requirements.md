# Equipment Request System Requirements

## Request data

Every request contains an employee ID and a natural-language request. The agent identifies the
requested item and uses MCP tools to retrieve the employee role, equipment history, and applicable
policy.

## Decisions

- Approve when the employee is below the role's quantity limit or an existing item has reached its
  refresh period.
- Deny when complete records show that the employee is at the quantity limit and the refresh period
  has not been reached.
- Escalate when the employee or role policy is missing, the item is not covered, the request is
  unclear, or the request involves a specialized, medical, accessibility, or exception case.

## Policies

- Standard employees: one laptop every four years, one monitor every three years, and one keyboard
  every two years.
- Software engineers: one laptop every three years, up to two monitors every three years, and one
  keyboard every two years.
- Managers: one laptop every two years, up to two monitors every three years, and one keyboard every
  two years.

The machine-readable source of these rules is `data/policies.json`.

## Reliability limits

- Maximum agent tool steps: 8.
- Maximum model attempts: 3.
- Maximum read-only MCP attempts: 3.
- MCP call timeout: 20 seconds.
- The side-effecting review tool is called once per agent attempt and uses an idempotent request ID.
- Reaching a safety limit produces a human escalation instead of an unsupported decision.
