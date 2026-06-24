/* address: 0x005113f0 */
/* name: CWeaponRound__SetReaderFromGlobalListByIndex */
/* signature: void __thiscall CWeaponRound__SetReaderFromGlobalListByIndex(void * this, int param_1, int param_2) */


void __thiscall CWeaponRound__SetReaderFromGlobalListByIndex(void *this,int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  iVar3 = 0;
  piVar1 = (int *)*DAT_008553f0;
  DAT_008553f0[2] = (int)piVar1;
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while (iVar2 != 0) {
    if (iVar3 == param_1) goto LAB_00511435;
    iVar3 = iVar3 + 1;
    piVar1 = *(int **)(DAT_008553f0[2] + 4);
    DAT_008553f0[2] = (int)piVar1;
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  iVar2 = 0;
LAB_00511435:
  *(int *)((int)this + 0x18) = iVar2;
  return;
}
