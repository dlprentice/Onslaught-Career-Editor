/* address: 0x004a45c0 */
/* name: CMenuItemRange__Init */
/* signature: undefined CMenuItemRange__Init(void) */


undefined4 * __thiscall
CMenuItemRange__Init
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
          undefined4 param_5,undefined4 param_6)

{
  param_1[1] = param_2;
  CSPtrSet__Init(param_1 + 2);
  param_1[7] = param_3;
  param_1[8] = param_4;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[10] = param_5;
  param_1[0xb] = param_6;
  *param_1 = &PTR_CMenuItemRange__ScalarDestructor_005dc650;
  return param_1;
}
