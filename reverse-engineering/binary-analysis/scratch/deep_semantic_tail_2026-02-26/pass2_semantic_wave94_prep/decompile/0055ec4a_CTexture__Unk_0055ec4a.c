/* address: 0x0055ec4a */
/* name: CTexture__Unk_0055ec4a */
/* signature: void __cdecl CTexture__Unk_0055ec4a(uint param_1) */


void __cdecl CTexture__Unk_0055ec4a(uint param_1)

{
  int *piVar1;
  uint dwBytes;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5af8;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  if (DAT_009d35e8 == 3) {
    ExceptionList = &local_14;
    if (param_1 <= DAT_009d35e0) {
      ExceptionList = &local_14;
      CDXTexture__Helper_00561179(9);
      local_8 = 0;
      piVar1 = CTexture__Unk_0056668d((void *)param_1);
      local_8 = 0xffffffff;
      CTexture__Helper_0055ecb1();
      if (piVar1 != (int *)0x0) {
        ExceptionList = local_14;
        return;
      }
    }
  }
  else {
    ExceptionList = &local_14;
    if (DAT_009d35e8 == 2) {
      if (param_1 == 0) {
        dwBytes = 0x10;
      }
      else {
        dwBytes = param_1 + 0xf & 0xfffffff0;
      }
      ExceptionList = &local_14;
      if (dwBytes <= DAT_00655da4) {
        ExceptionList = &local_14;
        CDXTexture__Helper_00561179(9);
        local_8 = 1;
        piVar1 = CTexture__Unk_00567130(dwBytes >> 4);
        local_8 = 0xffffffff;
        CTexture__Helper_0055ed10();
        if (piVar1 != (int *)0x0) {
          ExceptionList = local_14;
          return;
        }
      }
      goto LAB_0055ed29;
    }
  }
  if (param_1 == 0) {
    param_1 = 1;
  }
  dwBytes = param_1 + 0xf & 0xfffffff0;
LAB_0055ed29:
  HeapAlloc(DAT_009d35e4,0,dwBytes);
  ExceptionList = local_14;
  return;
}
