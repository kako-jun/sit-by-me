# Battle sword candidate previews

All 20 sword cutouts are visual candidates, not final historical replicas or game-design approvals. The matrices place each character's separate sword layer in front of the slash pose; white and dark backgrounds expose different alpha-edge issues. Slash transforms are recorded in the matching `assets/images/weapons/Cxxx/Cxxx-blade-candidates.json` file.

Current character previews:

- C001: 7 generations × 5 swords
- C002: 10 generations/structures × 5 swords
- C003: 5 generations × 5 swords
- C004: 5 generations × 5 swords

The current matrices omit trail layers. Per user direction, the five older C001 broad curved trail assets are archived as unused legacy candidates.

Battle-pose matrices (`Cxxx-battle-pose-matrix-{white,dark}.png`, C002-C004): representative sets x two swords (all sets x all five swords x all poses were checked for blade-tip clipping by script, not shown), columns ready / swing-windup / slash / swing-followthrough / special / step. The transforms behind them are the per-character `assets/images/characters/Cxxx/battle-layers.json` (same schema as C001; `step` of wheelchair sets has no sword).

C001 swing (#165): `C001-swing-matrix-{white,dark}.png` shows the 7 sets x (swing-windup, swing-followthrough) x 2 swords (Odenta, Onimaru); all 7 sets x 5 swords were clip-checked by script (blade tip at least 2px inside all four edges). `C001-swing-5frame-baseline.png` lines up idle / ready / swing-windup / slash / swing-followthrough on one ground line per set to show continuous person size.
