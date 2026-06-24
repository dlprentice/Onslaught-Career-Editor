/* address: 0x00414520 */
/* name: CGeneralVolume__GetCurrentEntryDistanceProgressRatio */
/* signature: double __fastcall CGeneralVolume__GetCurrentEntryDistanceProgressRatio(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__GetCurrentEntryDistanceProgressRatio(void *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int local_4;

  iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  if (iVar1 == 0) {
    return (double)_DAT_005d856c;
  }
  iVar5 = 0;
  iVar2 = 0;
  piVar3 = (int *)(*(int *)(iVar1 + 0xa4) + 0xc);
  piVar4 = piVar3;
  do {
    if (*piVar4 != -1) {
      iVar5 = iVar2;
    }
    iVar2 = iVar2 + 100;
    piVar4 = piVar4 + 1;
  } while (iVar2 < 500);
  if (iVar5 != 0) {
    local_4 = 0;
    iVar5 = 0;
    do {
      if (*piVar3 != -1) {
        local_4 = iVar5;
      }
      iVar5 = iVar5 + 100;
      piVar3 = piVar3 + 1;
    } while (iVar5 < 500);
    return (double)(*(float *)(iVar1 + 0x60) / (float)local_4);
  }
  return (double)_DAT_005d856c;
}
