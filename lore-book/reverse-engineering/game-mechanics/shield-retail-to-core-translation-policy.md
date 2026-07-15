# Retail → Core translation policy (shield regen/drain)

Status: **draft — blocked on dual-accept**  
Depends on: shield rate dual-accept (not landed)

## Measured retail input (pending)

Walker shield regen and optional damage drain from receipt-bound samples of
`BattleEngine+0x100` (hypothesis paired with energy `+0xFC`).

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Core candidates | `WalkerShieldRegenerationPerTick` |

## Explicit non-claims

- Draft only; no Core constant change authorized.
- Source shield-efficiency and mirror-from-energy rules are not dual-accepted rates.
