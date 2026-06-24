/* address: 0x004a1270 */
/* name: CMonitor__SelectNearestHostileTargetReader */
/* signature: void __fastcall CMonitor__SelectNearestHostileTargetReader(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__SelectNearestHostileTargetReader(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int *piVar7;
  int iVar8;
  int *to_read;
  float10 fVar9;
  float10 fVar10;
  float local_4;

  CGenericActiveReader__SetReader((void *)(param_1 + 0x44),(void *)0x0);
  iVar8 = *(int *)(param_1 + 0x18);
  iVar8 = CMapWho__GetFirstEntryWithinRadius
                    (*(undefined4 *)(iVar8 + 0x1c),*(undefined4 *)(iVar8 + 0x20),
                     *(undefined4 *)(iVar8 + 0x24),*(undefined4 *)(iVar8 + 0x28),0x40000000);
  local_4 = 999999.0;
  while (iVar8 != 0) {
    to_read = (int *)CMapWhoEntry__GetOwner();
    if ((((to_read != (int *)0x0) && (piVar7 = *(int **)(param_1 + 0x18), to_read != piVar7)) &&
        ((to_read[0xd] & 0x80000U) == 0)) && ((to_read[0xd] & 0x20800U) != 0)) {
      fVar1 = (float)to_read[7];
      fVar2 = (float)piVar7[7];
      fVar3 = (float)to_read[8];
      fVar4 = (float)piVar7[8];
      fVar5 = (float)to_read[9];
      fVar6 = (float)piVar7[9];
      fVar9 = (float10)(**(code **)(*piVar7 + 0x40))();
      fVar10 = (float10)(**(code **)(*to_read + 0x40))();
      fVar10 = (float10)(float)((float10)SQRT((fVar1 - fVar2) * (fVar1 - fVar2) +
                                              (fVar5 - fVar6) * (fVar5 - fVar6) +
                                              (fVar3 - fVar4) * (fVar3 - fVar4)) - fVar9) - fVar10;
      fVar1 = (float)fVar10;
      if ((fVar10 < (float10)local_4) && (fVar1 < _DAT_005d8568)) {
        CGenericActiveReader__SetReader((void *)(param_1 + 0x44),to_read);
        local_4 = fVar1;
      }
    }
    iVar8 = CMapWho__GetNextEntryWithinRadius();
  }
  return;
}
