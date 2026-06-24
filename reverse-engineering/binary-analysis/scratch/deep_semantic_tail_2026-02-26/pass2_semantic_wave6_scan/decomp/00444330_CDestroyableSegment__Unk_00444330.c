/* address: 0x00444330 */
/* name: CDestroyableSegment__Unk_00444330 */
/* signature: double __fastcall CDestroyableSegment__Unk_00444330(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CDestroyableSegment__Unk_00444330(int param_1)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  double dVar4;

  iVar3 = *(int *)(param_1 + 8);
  bVar1 = true;
  if (0 < iVar3) {
    piVar2 = *(int **)(param_1 + 4);
    do {
      if ((*piVar2 != 0) && (*(int *)(*piVar2 + 0x1c) == 1)) {
        bVar1 = false;
      }
      piVar2 = piVar2 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    if (!bVar1) {
      dVar4 = CDestroyableSegment__Helper_00442890(*(void **)(param_1 + 0xc));
      return dVar4;
    }
  }
  return (double)_DAT_005d8568;
}
