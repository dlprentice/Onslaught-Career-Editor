/* address: 0x004e49f0 */
/* name: CUnit__Unk_004e49f0 */
/* signature: int __fastcall CUnit__Unk_004e49f0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnit__Unk_004e49f0(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;

  if (*(int *)(param_1 + 0x448) != 0) {
    iVar4 = CMapWho__GetFirstEntryWithinRadius
                      (*(float *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x20),
                       *(undefined4 *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x28),0x3f800000);
    while( true ) {
      if (iVar4 == 0) {
        return 1;
      }
      iVar4 = CMapWhoEntry__GetOwner();
      if ((((iVar4 != 0) && ((*(uint *)(iVar4 + 0x34) & 0x10) != 0)) &&
          ((*(uint *)(iVar4 + 0x34) & 0x84000) == 0)) &&
         (fVar1 = *(float *)(iVar4 + 0x1c) - *(float *)(param_1 + 0x1c),
         fVar2 = *(float *)(iVar4 + 0x20) - *(float *)(param_1 + 0x20),
         fVar3 = *(float *)(iVar4 + 0x24) - *(float *)(param_1 + 0x24),
         fVar2 * fVar2 + fVar1 * fVar1 + fVar3 * fVar3 < _DAT_005d8bc0)) break;
      iVar4 = CMapWho__GetNextEntryWithinRadius();
    }
  }
  return 0;
}
