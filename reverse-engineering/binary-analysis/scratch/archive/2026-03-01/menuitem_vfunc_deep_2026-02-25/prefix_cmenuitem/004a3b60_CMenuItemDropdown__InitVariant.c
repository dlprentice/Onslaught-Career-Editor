/* address: 0x004a3b60 */
/* name: CMenuItemDropdown__InitVariant */
/* signature: undefined CMenuItemDropdown__InitVariant(void) */


void __thiscall
CMenuItemDropdown__InitVariant
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  param_1[1] = param_3;
  param_1[6] = param_2;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 1;
  param_1[5] = 0xffd6d6d6;
  *(undefined1 *)((int)param_1 + 0x25) = param_4;
  *(undefined1 *)(param_1 + 9) = 0;
  *param_1 = &PTR_VFuncSlot_00_004d0490_005dc5c4;
  return;
}
