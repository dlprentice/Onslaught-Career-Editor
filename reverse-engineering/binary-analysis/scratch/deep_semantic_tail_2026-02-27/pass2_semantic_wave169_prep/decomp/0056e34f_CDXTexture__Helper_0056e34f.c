/* address: 0x0056e34f */
/* name: CDXTexture__Helper_0056e34f */
/* signature: int __cdecl CDXTexture__Helper_0056e34f(int param_1, int param_2, int param_3, int param_4, uint param_5) */


int __cdecl
CDXTexture__Helper_0056e34f(int param_1,int param_2,int param_3,int param_4,uint param_5)

{
  int iVar1;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e69f8;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  ExceptionList = &local_14;
  if (DAT_009d0c30 == 0) {
    ExceptionList = &local_14;
    iVar1 = GetLocaleInfoW(0,1,(LPWSTR)0x0,0);
    if (iVar1 == 0) {
      iVar1 = GetLocaleInfoA(0,1,(LPSTR)0x0,0);
      if (iVar1 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      DAT_009d0c30 = 2;
    }
    else {
      DAT_009d0c30 = 1;
    }
  }
  if (DAT_009d0c30 != 1) {
    if (DAT_009d0c30 == 2) {
      if (param_5 == 0) {
        param_5 = DAT_009d09a8;
      }
      iVar1 = GetLocaleInfoA(param_1,param_2,(LPSTR)0x0,0);
      if (iVar1 != 0) {
        local_8 = 0;
        CRT__AllocaProbe();
        local_8 = 0xffffffff;
        if ((&stack0x00000000 != (undefined1 *)0x34) &&
           (iVar1 = GetLocaleInfoA(param_1,param_2,&stack0xffffffcc,iVar1), iVar1 != 0)) {
          if (param_4 == 0) {
            param_4 = 0;
            param_3 = 0;
          }
          iVar1 = MultiByteToWideChar(param_5,1,&stack0xffffffcc,-1,(LPWSTR)param_3,param_4);
          ExceptionList = local_14;
          return iVar1;
        }
      }
    }
    ExceptionList = local_14;
    return 0;
  }
  iVar1 = GetLocaleInfoW(param_1,param_2,(LPWSTR)param_3,param_4);
  ExceptionList = local_14;
  return iVar1;
}
