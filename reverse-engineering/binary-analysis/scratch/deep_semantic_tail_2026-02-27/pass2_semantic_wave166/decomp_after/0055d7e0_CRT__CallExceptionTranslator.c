/* address: 0x0055d7e0 */
/* name: CRT__CallExceptionTranslator */
/* signature: int CRT__CallExceptionTranslator(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__CallExceptionTranslator(void)

{
  int iVar1;
  undefined4 *in_stack_00000004;
  undefined4 uVar2;
  undefined1 *puVar3;
  undefined1 local_34 [8];
  undefined4 *local_2c;
  code *local_28;
  undefined4 local_14;
  undefined1 *local_10;
  undefined1 *local_c;
  int local_8;

  local_c = &stack0xfffffffc;
  local_10 = &stack0xffffffbc;
  local_28 = CRT__SehFilterCppException;
  local_8 = 0;
  local_14 = 0x55d868;
  local_2c = ExceptionList;
  ExceptionList = &local_2c;
  puVar3 = local_34;
  uVar2 = *in_stack_00000004;
  iVar1 = CTexture__Helper_00560b93();
  (**(code **)(iVar1 + 0x68))(uVar2,puVar3);
  if (local_8 != 0) {
    *local_2c = *(undefined4 *)ExceptionList;
  }
  ExceptionList = local_2c;
  return 0;
}
