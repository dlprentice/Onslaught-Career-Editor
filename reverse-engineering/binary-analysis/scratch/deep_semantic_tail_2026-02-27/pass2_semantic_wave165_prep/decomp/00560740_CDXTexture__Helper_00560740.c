/* address: 0x00560740 */
/* name: CDXTexture__Helper_00560740 */
/* signature: int __cdecl CDXTexture__Helper_00560740(void * param_1, void * param_2, void * param_3) */


int __cdecl CDXTexture__Helper_00560740(void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5b48;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  ExceptionList = &local_14;
  CTexture__Helper_00560b93();
  CTexture__Helper_00560b93();
  iVar1 = CTexture__Helper_00560b93();
  *(void **)(iVar1 + 0x6c) = param_1;
  iVar1 = CTexture__Helper_00560b93();
  *(void **)(iVar1 + 0x70) = param_3;
  local_8 = 1;
  iVar1 = CRT__SehInvokeCallSettingFrame12();
  local_8 = 0xffffffff;
  CDXTexture__Helper_0056080d();
  ExceptionList = local_14;
  return iVar1;
}
