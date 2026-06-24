/* address: 0x0055d767 */
/* name: CRT__SehInvokeCallSettingFrame12 */
/* signature: int CRT__SehInvokeCallSettingFrame12(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__SehInvokeCallSettingFrame12(void)

{
  int iVar1;
  undefined4 in_stack_00000004;
  undefined4 in_stack_0000000c;
  int in_stack_00000010;
  undefined4 in_stack_00000014;
  void *local_18;
  code *local_14;
  int local_8;

  local_14 = CRT__SehCallback_Call_005602d2;
  local_8 = in_stack_00000010 + 1;
  local_18 = ExceptionList;
  ExceptionList = &local_18;
  iVar1 = __CallSettingFrame_12(in_stack_0000000c,in_stack_00000004,in_stack_00000014);
  ExceptionList = local_18;
  return iVar1;
}
