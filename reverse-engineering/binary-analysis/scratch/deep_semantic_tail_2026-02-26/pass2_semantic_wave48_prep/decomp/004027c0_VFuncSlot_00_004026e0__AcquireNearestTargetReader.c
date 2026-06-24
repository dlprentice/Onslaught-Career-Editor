/* address: 0x004027c0 */
/* name: VFuncSlot_00_004026e0__AcquireNearestTargetReader */
/* signature: void __fastcall VFuncSlot_00_004026e0__AcquireNearestTargetReader(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall VFuncSlot_00_004026e0__AcquireNearestTargetReader(int param_1)

{
  float fVar1;
  int iVar2;
  int *to_read;
  float10 fVar3;
  float10 fVar4;
  float10 fVar5;
  float10 fVar6;
  float10 fVar7;
  float local_8;

  CGenericActiveReader__SetReader((void *)(param_1 + 0x2c),(void *)0x0);
  iVar2 = *(int *)(param_1 + 0x18);
  iVar2 = CMapWho__GetFirstEntryWithinRadius
                    (*(undefined4 *)(iVar2 + 0x1c),*(undefined4 *)(iVar2 + 0x20),
                     *(undefined4 *)(iVar2 + 0x24),*(undefined4 *)(iVar2 + 0x28),0x41f00000);
  local_8 = 999999.0;
  fVar3 = (float10)(**(code **)(**(int **)(param_1 + 0x18) + 0x40))();
  while (iVar2 != 0) {
    to_read = (int *)CMapWhoEntry__GetOwner();
    if (((to_read != (int *)0x0) && (to_read != *(int **)(param_1 + 0x18))) &&
       ((*(byte *)(to_read + 0xd) & 4) == 0)) {
      fVar4 = (float10)(**(code **)(*to_read + 0x40))();
      iVar2 = *(int *)(param_1 + 0x18);
      fVar5 = (float10)(float)to_read[7] - (float10)*(float *)(iVar2 + 0x1c);
      fVar6 = (float10)(float)to_read[8] - (float10)*(float *)(iVar2 + 0x20);
      fVar7 = (float10)(float)to_read[9] - (float10)*(float *)(iVar2 + 0x24);
      fVar1 = (float)(((fVar6 * fVar6 + fVar5 * fVar5 + fVar7 * fVar7) - fVar4 * fVar4) -
                     (float10)(float)(fVar3 * fVar3));
      if ((fVar1 < local_8) && (fVar1 < _DAT_005d85f4)) {
        CGenericActiveReader__SetReader((void *)(param_1 + 0x2c),to_read);
        local_8 = fVar1;
      }
    }
    iVar2 = CMapWho__GetNextEntryWithinRadius();
  }
  return;
}
