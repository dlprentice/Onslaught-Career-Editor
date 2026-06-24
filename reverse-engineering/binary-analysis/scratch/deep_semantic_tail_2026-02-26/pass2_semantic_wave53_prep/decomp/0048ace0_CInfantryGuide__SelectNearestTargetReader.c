/* address: 0x0048ace0 */
/* name: CInfantryGuide__SelectNearestTargetReader */
/* signature: void __fastcall CInfantryGuide__SelectNearestTargetReader(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CInfantryGuide__SelectNearestTargetReader(int param_1)

{
  void *this;
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int *piVar7;
  bool bVar8;
  int iVar9;
  int *to_read;
  float10 fVar10;
  float local_28;

  this = (void *)(param_1 + 0x44);
  CGenericActiveReader__SetReader(this,(void *)0x0);
  iVar9 = *(int *)(param_1 + 0x18);
  iVar9 = CMapWho__GetFirstEntryWithinRadius
                    (*(undefined4 *)(iVar9 + 0x1c),*(undefined4 *)(iVar9 + 0x20),
                     *(undefined4 *)(iVar9 + 0x24),*(undefined4 *)(iVar9 + 0x28),0x3f800000);
  bVar8 = false;
  local_28 = 999999.0;
  while (iVar9 != 0) {
    to_read = (int *)CMapWhoEntry__GetOwner();
    if ((to_read != (int *)0x0) && (piVar7 = *(int **)(param_1 + 0x18), to_read != piVar7)) {
      if (((to_read[0xd] & 0x20800U) == 0) || (to_read[0x4e] == piVar7[0x4e])) {
        if (((!bVar8) && ((to_read[0xd] & 0x4000U) != 0)) && ((*(byte *)(to_read + 0xb) & 4) == 0))
        {
          fVar1 = (float)to_read[7];
          fVar2 = (float)piVar7[7];
          fVar3 = (float)to_read[8];
          fVar4 = (float)piVar7[8];
          fVar5 = (float)to_read[9];
          fVar6 = (float)piVar7[9];
          fVar10 = (float10)(**(code **)(*to_read + 0x40))();
          fVar1 = (float)(((float10)(fVar5 - fVar6) * (float10)(fVar5 - fVar6) +
                          (float10)(fVar3 - fVar4) * (float10)(fVar3 - fVar4) +
                          (float10)(fVar1 - fVar2) * (float10)(fVar1 - fVar2)) - fVar10 * fVar10);
          if ((fVar1 < local_28) && (fVar1 < _DAT_005dbfd0)) {
            CGenericActiveReader__SetReader(this,to_read);
            local_28 = fVar1;
          }
        }
      }
      else {
        fVar1 = (float)to_read[7];
        fVar2 = (float)piVar7[7];
        fVar3 = (float)to_read[8];
        fVar4 = (float)piVar7[8];
        fVar5 = (float)to_read[9];
        fVar6 = (float)piVar7[9];
        fVar10 = (float10)(**(code **)(*to_read + 0x40))();
        fVar1 = (float)(((float10)(fVar3 - fVar4) * (float10)(fVar3 - fVar4) +
                        (float10)(fVar1 - fVar2) * (float10)(fVar1 - fVar2) +
                        (float10)(fVar5 - fVar6) * (float10)(fVar5 - fVar6)) - fVar10 * fVar10);
        if ((fVar1 < local_28) && (fVar1 < _DAT_005d8568)) {
          CGenericActiveReader__SetReader(this,to_read);
          bVar8 = true;
          local_28 = fVar1;
        }
      }
    }
    iVar9 = CMapWho__GetNextEntryWithinRadius();
  }
  return;
}
