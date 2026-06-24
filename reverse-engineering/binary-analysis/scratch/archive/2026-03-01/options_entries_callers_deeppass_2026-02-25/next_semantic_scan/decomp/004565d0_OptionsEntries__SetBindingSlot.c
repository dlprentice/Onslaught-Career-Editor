/* address: 0x004565d0 */
/* name: OptionsEntries__SetBindingSlot */
/* signature: undefined OptionsEntries__SetBindingSlot(void) */


void OptionsEntries__SetBindingSlot
               (int param_1,int param_2,int param_3,int param_4,undefined2 param_5,
               undefined2 param_6)

{
  int *piVar1;

  piVar1 = OptionsEntries__FindById(param_2);
  piVar1[param_1 * 3 + 2] = param_3;
  piVar1[param_1 * 3 + 3] = param_4;
  *(undefined2 *)(piVar1 + param_1 * 3 + 4) = param_5;
  *(undefined2 *)((int)piVar1 + param_1 * 0xc + 0x12) = param_6;
  return;
}
