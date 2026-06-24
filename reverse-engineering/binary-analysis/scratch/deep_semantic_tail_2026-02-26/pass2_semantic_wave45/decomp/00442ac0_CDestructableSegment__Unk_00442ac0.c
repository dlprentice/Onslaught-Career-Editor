/* address: 0x00442ac0 */
/* name: CDestructableSegment__Unk_00442ac0 */
/* signature: void __thiscall CDestructableSegment__Unk_00442ac0(void * this, int param_1, int param_2) */


void __thiscall CDestructableSegment__Unk_00442ac0(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int *piVar2;

  puVar1 = *(undefined4 **)((int)this + 0x24);
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while (piVar2 != (int *)0x0) {
    (**(code **)(*piVar2 + 0xc))(param_1,*(undefined4 *)(*(int *)((int)this + 0x3c) + 0x10));
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return;
}
