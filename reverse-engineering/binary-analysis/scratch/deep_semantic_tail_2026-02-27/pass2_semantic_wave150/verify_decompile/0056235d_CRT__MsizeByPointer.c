/* address: 0x0056235d */
/* name: CRT__MsizeByPointer */
/* signature: int __cdecl CRT__MsizeByPointer(int param_1) */


int __cdecl CRT__MsizeByPointer(int param_1)

{
  byte *pbVar1;
  SIZE_T SVar2;
  int iVar3;
  undefined1 local_30 [4];
  byte *local_2c;
  undefined1 local_28 [4];
  int local_24;
  byte *local_20;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5cc0;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  if (DAT_009d35e8 == 3) {
    ExceptionList = &local_14;
    CDXTexture__Helper_00561179(9);
    local_8 = 0;
    local_20 = (byte *)CRT__FindSmallBlockHeapEntryForPtr(param_1);
    if (local_20 != (byte *)0x0) {
      local_24 = *(int *)(param_1 + -4) + -9;
    }
    iVar3 = local_24;
    local_8 = 0xffffffff;
    CDXTexture__Unk_005623c7();
    pbVar1 = local_20;
  }
  else {
    ExceptionList = &local_14;
    if (DAT_009d35e8 != 2) goto LAB_0056241b;
    ExceptionList = &local_14;
    CDXTexture__Helper_00561179(9);
    local_8 = 1;
    local_2c = (byte *)CDXTexture__Helper_00567094((void *)param_1,local_30,local_28);
    if (local_2c != (byte *)0x0) {
      local_24 = (uint)*local_2c << 4;
    }
    iVar3 = local_24;
    local_8 = 0xffffffff;
    CDXTexture__Unk_00562442();
    pbVar1 = local_2c;
  }
  if (pbVar1 != (byte *)0x0) {
    ExceptionList = local_14;
    return iVar3;
  }
LAB_0056241b:
  SVar2 = HeapSize(DAT_009d35e4,0,(LPCVOID)param_1);
  ExceptionList = local_14;
  return SVar2;
}
