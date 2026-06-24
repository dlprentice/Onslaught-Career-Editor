/* address: 0x004a4e10 */
/* name: CMenuItemRangeVariant__Init */
/* signature: undefined CMenuItemRangeVariant__Init(void) */


undefined4 * __thiscall
CMenuItemRangeVariant__Init
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
  *param_1 = &PTR_CMenuItemRangeVariant__ScalarDestructor_005dc664;
  return param_1;
}
