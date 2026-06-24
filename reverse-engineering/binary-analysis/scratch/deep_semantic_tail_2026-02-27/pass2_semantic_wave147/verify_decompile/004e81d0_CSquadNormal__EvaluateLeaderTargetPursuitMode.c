/* address: 0x004e81d0 */
/* name: CSquadNormal__EvaluateLeaderTargetPursuitMode */
/* signature: int __fastcall CSquadNormal__EvaluateLeaderTargetPursuitMode(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CSquadNormal__EvaluateLeaderTargetPursuitMode(void *param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  void *this;
  int *piVar4;
  float *pfVar5;
  uint uVar6;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  undefined1 *puVar7;
  int iVar8;
  float fVar9;

  iVar1 = *(int *)((int)param_1 + 0xc4);
  if (iVar1 != 0) {
    iVar8 = *(int *)(iVar1 + 0x1c);
    this = (void *)(**(code **)(*(int *)param_1 + 300))
                             (iVar8,*(undefined4 *)(iVar1 + 0x20),*(undefined4 *)(iVar1 + 0x24),
                              *(undefined4 *)(iVar1 + 0x28));
    if (this == (void *)0x0) {
      return 1;
    }
    piVar4 = *(int **)((int)param_1 + 0xc4);
    if ((piVar4[0xd] & 0x20000000U) == 0) {
      if ((piVar4[0xd] & 0x10U) == 0) {
        return 0;
      }
    }
    else {
      piVar4 = (int *)(**(code **)(*piVar4 + 300))
                                (*(undefined4 *)((int)this + 0x1c),*(undefined4 *)((int)this + 0x20)
                                 ,*(undefined4 *)((int)this + 0x24),
                                 *(undefined4 *)((int)this + 0x28));
    }
    if (piVar4 == (int *)0x0) {
      return 0;
    }
    CSquadNormal__Helper_004fb840(this,piVar4,iVar8);
    iVar1 = *(int *)((int)param_1 + 0xc4);
    puVar7 = &stack0xffffffe0;
    pfVar5 = (float *)(**(code **)(*(int *)param_1 + 0x120))();
    fVar9 = *(float *)(iVar1 + 0x1c) - *pfVar5;
    fVar2 = *(float *)(iVar1 + 0x20) - pfVar5[1];
    fVar3 = *(float *)(iVar1 + 0x24) - pfVar5[2];
    fVar9 = SQRT(fVar9 * fVar9 + fVar3 * fVar3 + fVar2 * fVar2);
    CSquadNormal__Helper_004fb780();
    if ((float10)fVar9 < extraout_ST0 * (float10)_DAT_005db4ac) {
      return 2;
    }
    CSquadNormal__Helper_004fb7e0();
    if (((float10)fVar9 <= extraout_ST0_00 * (float10)_DAT_005d8600) &&
       (uVar6 = CUnit__CanFireAtTarget_BallisticArcB(this,(int)piVar4,puVar7), uVar6 != 0)) {
      return 0;
    }
  }
  return 1;
}
