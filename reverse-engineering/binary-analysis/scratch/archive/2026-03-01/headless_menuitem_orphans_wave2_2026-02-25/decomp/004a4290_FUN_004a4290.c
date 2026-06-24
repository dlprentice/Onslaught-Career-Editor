/* address: 0x004a4290 */
/* name: FUN_004a4290 */
/* signature: undefined FUN_004a4290(void) */


void __thiscall FUN_004a4290(int param_1,undefined4 param_2,int param_3)

{
  undefined4 *puVar1;
  int *piVar2;

  if (param_3 == 0x2c) {
    DAT_00704868 = DAT_00704868 + 1;
    puVar1 = *(undefined4 **)(*(int *)(param_1 + 0x1c) + 8);
    *(undefined4 **)(*(int *)(param_1 + 0x1c) + 0x10) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
    while (piVar2 != (int *)0x0) {
      (**(code **)(*piVar2 + 0x2c))();
      puVar1 = *(undefined4 **)(*(int *)(*(int *)(param_1 + 0x1c) + 0x10) + 4);
      *(undefined4 **)(*(int *)(param_1 + 0x1c) + 0x10) = puVar1;
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
