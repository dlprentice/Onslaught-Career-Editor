/* address: 0x00501800 */
/* name: CVertexShader__CVertexShader */
/* signature: undefined CVertexShader__CVertexShader(void) */


undefined4 * __fastcall CVertexShader__CVertexShader(undefined4 *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d56d8;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *param_1 = &PTR_CVertexShader__VFunc_00_00501890_005dfbc4;
  puVar2 = param_1 + 2;
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  local_4 = 0;
  param_1[10] = 0;
  param_1[0xc] = 0;
  CShaderBase__Init((int)param_1);
  param_1[0x16] = DAT_00854e68;
  DAT_00854e68 = param_1;
  *(undefined1 *)(param_1 + 0xd) = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0xb] = 9;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  ExceptionList = local_c;
  return param_1;
}
