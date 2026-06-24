/* address: 0x004a4630 */
/* name: CMenuItemRange__ResetIterator */
/* signature: undefined CMenuItemRange__ResetIterator(void) */


void __fastcall CMenuItemRange__ResetIterator(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;

  *(undefined4 *)(param_1 + 0x18) = 0;
  puVar1 = *(undefined4 **)(param_1 + 8);
  *(undefined4 **)(param_1 + 0x10) = puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while (piVar2 != (int *)0x0) {
    (**(code **)(*piVar2 + 0x30))();
    puVar1 = *(undefined4 **)(*(int *)(param_1 + 0x10) + 4);
    *(undefined4 **)(param_1 + 0x10) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return;
}
