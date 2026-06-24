/* address: 0x004a3be0 */
/* name: FUN_004a3be0 */
/* signature: undefined FUN_004a3be0(void) */


void __thiscall FUN_004a3be0(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  if ((param_4 != 0) && (DAT_0070486c == 0)) {
    DAT_00704874 = param_2;
    DAT_00704870 = param_3;
    DAT_0070486c = param_1;
    return;
  }
  CMenuItemDropdown__Render(param_2,param_3,0);
  return;
}
