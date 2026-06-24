/* address: 0x00560c5b */
/* name: CDXTexture__InvokeGlobalCleanupCallbackAndFinalize */
/* signature: void CDXTexture__InvokeGlobalCleanupCallbackAndFinalize(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__InvokeGlobalCleanupCallbackAndFinalize(void)

{
  void *pvStack_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  puStack_c = &DAT_005e5b98;
  puStack_10 = &LAB_0056127c;
  pvStack_14 = ExceptionList;
  ExceptionList = &pvStack_14;
  if (PTR_CDXTexture__InvokeTlsCleanupCallbackAndFinalize_00653654 != (undefined *)0x0) {
    local_8 = 1;
    ExceptionList = &pvStack_14;
    (*(code *)PTR_CDXTexture__InvokeTlsCleanupCallbackAndFinalize_00653654)();
  }
  local_8 = 0xffffffff;
  CDXTexture__InvokeTlsCleanupCallbackAndFinalize();
  return;
}
