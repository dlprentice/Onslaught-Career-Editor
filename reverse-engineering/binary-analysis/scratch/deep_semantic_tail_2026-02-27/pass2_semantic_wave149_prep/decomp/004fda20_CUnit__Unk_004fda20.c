/* address: 0x004fda20 */
/* name: CUnit__Unk_004fda20 */
/* signature: void __thiscall CUnit__Unk_004fda20(void * this, int param_1, int param_2) */


void __thiscall CUnit__Unk_004fda20(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int unaff_EDI;

  if ((*(int **)((int)this + 0x148) != (int *)0x0) && (param_1 != 0)) {
    (**(code **)(**(int **)((int)this + 0x148) + 0x154))(*(undefined4 *)(param_1 + 0x148));
  }
  if (*(void **)((int)this + 0x13c) != (void *)0x0) {
    CSquadNormal__Helper_004ffdd0(*(void **)((int)this + 0x13c),param_1,(void *)0x1,unaff_EDI);
  }
  puVar1 = *(undefined4 **)((int)this + 0x19c);
  if (puVar1 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    puVar2 = (undefined4 *)*puVar1;
  }
  while (puVar2 != (undefined4 *)0x0) {
    if ((void *)*puVar2 != (void *)0x0) {
      CUnit__Unk_004fda20((void *)*puVar2,param_1,unaff_EDI);
    }
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      puVar2 = (undefined4 *)0x0;
    }
    else {
      puVar2 = (undefined4 *)*puVar1;
    }
  }
  return;
}
