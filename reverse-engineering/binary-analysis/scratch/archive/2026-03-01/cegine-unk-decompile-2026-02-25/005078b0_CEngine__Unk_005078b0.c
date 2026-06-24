/* address: 0x005078b0 */
/* name: CEngine__Unk_005078b0 */
/* signature: int __thiscall CEngine__Unk_005078b0(void * this, int param_1, int param_2) */


int __thiscall CEngine__Unk_005078b0(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;

  puVar1 = *(undefined4 **)((int)this + 0x4c);
  iVar3 = 0;
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while( true ) {
    if (piVar2 == (int *)0x0) {
      return 0;
    }
    if (iVar3 == param_1) break;
    puVar1 = (undefined4 *)puVar1[1];
    iVar3 = iVar3 + 1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return *piVar2;
}
