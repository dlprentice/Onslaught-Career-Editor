/* address: 0x0053f0a0 */
/* name: CVBufTexture__Unk_0053f0a0 */
/* signature: void __fastcall CVBufTexture__Unk_0053f0a0(void * param_1) */


void __fastcall CVBufTexture__Unk_0053f0a0(void *param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d77c8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  DeviceObject__ctor_like_00512d50();
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}
