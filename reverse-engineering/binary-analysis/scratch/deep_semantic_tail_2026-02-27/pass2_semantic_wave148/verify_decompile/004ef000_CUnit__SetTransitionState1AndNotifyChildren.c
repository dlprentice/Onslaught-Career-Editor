/* address: 0x004ef000 */
/* name: CUnit__SetTransitionState1AndNotifyChildren */
/* signature: void __fastcall CUnit__SetTransitionState1AndNotifyChildren(int param_1) */


void __fastcall CUnit__SetTransitionState1AndNotifyChildren(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;

  if ((*(int *)(param_1 + 0x250) == 2) || (*(int *)(param_1 + 0x250) == 3)) {
    *(undefined4 *)(param_1 + 0x250) = 1;
    puVar1 = *(undefined4 **)(param_1 + 0x19c);
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
    while (piVar2 != (int *)0x0) {
      if ((int *)*piVar2 != (int *)0x0) {
        (**(code **)(*(int *)*piVar2 + 0x5c))();
      }
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        piVar2 = (int *)0x0;
      }
      else {
        piVar2 = (int *)*puVar1;
      }
    }
  }
  return;
}
