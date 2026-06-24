/* address: 0x004fdc20 */
/* name: CUnit__Unk_004fdc20 */
/* signature: void __fastcall CUnit__Unk_004fdc20(int param_1) */


void __fastcall CUnit__Unk_004fdc20(int param_1)

{
  int *piVar1;
  int iVar2;

  iVar2 = *(int *)(param_1 + 0x164);
  if (iVar2 == 0) {
    return;
  }
  if (*(int *)(param_1 + 0x138) == 0) {
    iVar2 = CUnit__Helper_00511510(iVar2);
    iVar2 = -iVar2;
  }
  else {
    if (*(int *)(param_1 + 0x138) != 1) goto LAB_004fdc57;
    iVar2 = CUnit__Helper_00511510(iVar2);
  }
  DAT_008a9b8c = DAT_008a9b8c + iVar2;
LAB_004fdc57:
  piVar1 = *(int **)(param_1 + 0x18c);
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while (iVar2 != 0) {
    CSpawnerThng__UpdateSpawnCount();
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  return;
}
