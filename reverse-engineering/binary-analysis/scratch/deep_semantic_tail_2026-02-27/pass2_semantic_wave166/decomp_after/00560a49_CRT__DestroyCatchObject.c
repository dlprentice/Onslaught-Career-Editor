/* address: 0x00560a49 */
/* name: CRT__DestroyCatchObject */
/* signature: void __cdecl CRT__DestroyCatchObject(int param_1) */


void __cdecl CRT__DestroyCatchObject(int param_1)

{
  void *pvVar1;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  puStack_c = &DAT_005e5b70;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  if ((param_1 != 0) && (pvVar1 = *(void **)(*(int *)(param_1 + 0x1c) + 4), pvVar1 != (void *)0x0))
  {
    local_8 = 0;
    ExceptionList = &local_14;
    CRT__InvokeCallbackWithLockGuards(*(int *)(param_1 + 0x18),pvVar1);
  }
  ExceptionList = local_14;
  return;
}
