/* address: 0x0055f085 */
/* name: CMeshCollisionVolume__Unk_0055f085 */
/* signature: void __cdecl CMeshCollisionVolume__Unk_0055f085(int param_1) */


void __cdecl CMeshCollisionVolume__Unk_0055f085(int param_1)

{
  void *pvVar1;
  int local_2c;
  void *local_28;
  int local_24;
  void *local_20;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5b10;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  if (param_1 == 0) {
    return;
  }
  if (DAT_009d35e8 == 3) {
    ExceptionList = &local_14;
    CDXTexture__Helper_00561179(9);
    local_8 = 0;
    local_20 = (void *)CRT__FindSmallBlockHeapEntryForPtr(param_1);
    if (local_20 != (void *)0x0) {
      CDXTexture__Helper_00566364(local_20,param_1);
    }
    local_8 = 0xffffffff;
    CMeshCollisionVolume__Unk_0055f0ef();
    pvVar1 = local_20;
  }
  else {
    ExceptionList = &local_14;
    if (DAT_009d35e8 != 2) goto LAB_0055f151;
    ExceptionList = &local_14;
    CDXTexture__Helper_00561179(9);
    local_8 = 1;
    local_28 = (void *)CDXTexture__Helper_00567094((void *)param_1,&local_2c,&local_24);
    if (local_28 != (void *)0x0) {
      CDXTexture__Unk_005670eb(local_2c,local_24,local_28);
    }
    local_8 = 0xffffffff;
    CMeshCollisionVolume__Unk_0055f147();
    pvVar1 = local_28;
  }
  if (pvVar1 != (void *)0x0) {
    ExceptionList = local_14;
    return;
  }
LAB_0055f151:
  HeapFree(DAT_009d35e4,0,(LPVOID)param_1);
  ExceptionList = local_14;
  return;
}
