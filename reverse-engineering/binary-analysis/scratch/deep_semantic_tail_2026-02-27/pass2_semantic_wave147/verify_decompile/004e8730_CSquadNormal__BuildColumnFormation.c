/* address: 0x004e8730 */
/* name: CSquadNormal__BuildColumnFormation */
/* signature: void __fastcall CSquadNormal__BuildColumnFormation(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CSquadNormal__BuildColumnFormation(void *param_1)

{
  float fVar1;
  undefined4 *puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int *piVar7;
  float unaff_EDI;
  int iVar8;
  bool bVar9;
  double dVar10;
  uint local_28;
  undefined8 local_20;
  undefined4 local_18;
  undefined4 local_14;

  CSquadNormal__PruneDeadMembersAndReschedule(param_1,(void *)0x0,unaff_EDI);
  if (*(float *)((int)param_1 + 0x104) != _DAT_005d856c) {
    iVar6 = 0;
    dVar10 = CRT__RoundToIntegerRespectingControlWord(SQRT((double)*(int *)((int)param_1 + 0xb4)));
    local_20 = (longlong)ROUND(dVar10);
    local_28 = (uint)local_20;
    if ((int)(uint)local_20 < 1) {
      local_28 = 1;
    }
    uVar3 = local_28 & 0x80000001;
    bVar9 = uVar3 == 0;
    if ((int)uVar3 < 0) {
      bVar9 = (uVar3 - 1 | 0xfffffffe) == 0xffffffff;
    }
    fVar1 = _DAT_005d856c;
    if (bVar9) {
      fVar1 = *(float *)((int)param_1 + 0x104);
    }
    piVar7 = *(int **)((int)param_1 + 0xa4);
    if (piVar7 == (int *)0x0) {
      iVar8 = 0;
    }
    else {
      iVar8 = *piVar7;
    }
    while (iVar8 != 0) {
      iVar4 = iVar6 / (int)local_28;
      local_20._4_4_ = (undefined4)((ulonglong)local_20 >> 0x20);
      local_20 = CONCAT44(local_20._4_4_,iVar4);
      uVar3 = iVar6 - iVar4 * local_28;
      uVar5 = uVar3 & 0x80000001;
      if ((int)uVar5 < 0) {
        uVar5 = (uVar5 - 1 | 0xfffffffe) + 1;
      }
      if (uVar5 == 1) {
        uVar3 = -uVar3 - 1;
      }
      iVar6 = iVar6 + 1;
      *(float *)(iVar8 + 4) = (float)(int)uVar3 * *(float *)((int)param_1 + 0x104) + fVar1;
      *(float *)(iVar8 + 8) = (float)iVar4 * *(float *)((int)param_1 + 0x104) * _DAT_005d95c0;
      piVar7 = (int *)piVar7[1];
      if (piVar7 == (int *)0x0) {
        iVar8 = 0;
      }
      else {
        iVar8 = *piVar7;
      }
    }
    *(undefined4 *)((int)param_1 + 0xbc) = 1;
  }
  iVar6 = CSquadNormal__ResolveFormationSlotConflicts((int)param_1);
  while (iVar6 == 0) {
    iVar6 = CSquadNormal__ResolveFormationSlotConflicts((int)param_1);
  }
  puVar2 = *(undefined4 **)((int)param_1 + 0xa4);
  if (puVar2 == (undefined4 *)0x0) {
    piVar7 = (int *)0x0;
  }
  else {
    piVar7 = (int *)*puVar2;
  }
  while (piVar7 != (int *)0x0) {
    if (*piVar7 != 0) {
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      (**(code **)(*(int *)*piVar7 + 0xf4))((uint)local_20,local_20._4_4_,local_18,local_14,0);
    }
    puVar2 = (undefined4 *)puVar2[1];
    if (puVar2 == (undefined4 *)0x0) {
      piVar7 = (int *)0x0;
    }
    else {
      piVar7 = (int *)*puVar2;
    }
  }
  return;
}
