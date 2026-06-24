/* address: 0x004fd8d0 */
/* name: CUnit__Unk_004fd8d0 */
/* signature: int * __thiscall CUnit__Unk_004fd8d0(void * this, int param_1, int param_2) */


int * __thiscall CUnit__Unk_004fd8d0(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int *piVar2;

  puVar1 = *(undefined4 **)((int)this + 0x19c);
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while( true ) {
    if (piVar2 == (int *)0x0) {
      return (int *)0x0;
    }
    if ((*piVar2 != 0) && (*(int *)(*piVar2 + 0x270) == param_1)) break;
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return piVar2;
}
