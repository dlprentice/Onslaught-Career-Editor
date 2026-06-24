/* address: 0x004121b0 */
/* name: CGeneralVolume__EntryIterator_GetSlotFillRatio */
/* signature: double __fastcall CGeneralVolume__EntryIterator_GetSlotFillRatio(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__EntryIterator_GetSlotFillRatio(void *param_1)

{
  int *piVar1;
  float fVar2;
  int iVar3;
  int iVar4;

  fVar2 = _DAT_005d856c;
  piVar1 = *(int **)param_1;
  iVar4 = 0;
  *(int **)((int)param_1 + 8) = piVar1;
  if (piVar1 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar1;
  }
  if (iVar3 != 0) {
    while (iVar4 != *(int *)((int)param_1 + 0x10)) {
      iVar4 = iVar4 + 1;
      piVar1 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *piVar1;
      }
      if (iVar3 == 0) {
        return (double)fVar2;
      }
    }
    if ((iVar3 != 0) &&
       (iVar4 = *(int *)(*(int *)(iVar3 + 0xa4) + 0x24),
       fVar2 = *(float *)(*(int *)((int)param_1 + 0x18) + 0x52c + iVar4 * 4) /
               *(float *)(*(int *)(*(int *)((int)param_1 + 0x18) + 0x4b0) + 0x88 + iVar4 * 4),
       _DAT_005d8568 < fVar2)) {
      fVar2 = _DAT_005d8568;
    }
  }
  return (double)fVar2;
}
