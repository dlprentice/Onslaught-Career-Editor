/* address: 0x00565ee0 */
/* name: CRT__LCMapStringA_Compat */
/* signature: int CRT__LCMapStringA_Compat(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__LCMapStringA_Compat(void)

{
  int iVar1;
  int iVar2;
  LCID in_stack_00000004;
  uint in_stack_00000008;
  LPCSTR in_stack_0000000c;
  int in_stack_00000010;
  LPWSTR in_stack_00000014;
  int in_stack_00000018;
  UINT in_stack_0000001c;
  int in_stack_00000020;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5e40;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  ExceptionList = &local_14;
  if (DAT_009d09b0 == 0) {
    ExceptionList = &local_14;
    iVar1 = LCMapStringW(0,0x100,L"",1,(LPWSTR)0x0,0);
    if (iVar1 == 0) {
      iVar1 = LCMapStringA(0,0x100,&DAT_00662b28,1,(LPSTR)0x0,0);
      if (iVar1 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      DAT_009d09b0 = 2;
    }
    else {
      DAT_009d09b0 = 1;
    }
  }
  if (0 < in_stack_00000010) {
    in_stack_00000010 = CDXTexture__Helper_0056e8aa(in_stack_0000000c,in_stack_00000010);
  }
  if (DAT_009d09b0 == 2) {
    iVar1 = LCMapStringA(in_stack_00000004,in_stack_00000008,in_stack_0000000c,in_stack_00000010,
                         (LPSTR)in_stack_00000014,in_stack_00000018);
    ExceptionList = local_14;
    return iVar1;
  }
  if (DAT_009d09b0 == 1) {
    if (in_stack_0000001c == 0) {
      in_stack_0000001c = DAT_009d09a8;
    }
    iVar1 = MultiByteToWideChar(in_stack_0000001c,(-(uint)(in_stack_00000020 != 0) & 8) + 1,
                                in_stack_0000000c,in_stack_00000010,(LPWSTR)0x0,0);
    if (iVar1 != 0) {
      local_8 = 0;
      CRT__AllocaProbe();
      local_8 = 0xffffffff;
      if ((&stack0x00000000 != (undefined1 *)0x3c) &&
         (iVar2 = MultiByteToWideChar(in_stack_0000001c,1,in_stack_0000000c,in_stack_00000010,
                                      (LPWSTR)&stack0xffffffc4,iVar1), iVar2 != 0)) {
        iVar2 = LCMapStringW(in_stack_00000004,in_stack_00000008,(LPCWSTR)&stack0xffffffc4,iVar1,
                             (LPWSTR)0x0,0);
        if (iVar2 != 0) {
          if ((in_stack_00000008 & 0x400) == 0) {
            local_8 = 1;
            CRT__AllocaProbe();
            local_8 = 0xffffffff;
            if (&stack0x00000000 == (undefined1 *)0x3c) {
              ExceptionList = local_14;
              return 0;
            }
            iVar1 = LCMapStringW(in_stack_00000004,in_stack_00000008,(LPCWSTR)&stack0xffffffc4,iVar1
                                 ,(LPWSTR)&stack0xffffffc4,iVar2);
            if (iVar1 == 0) {
              ExceptionList = local_14;
              return 0;
            }
            if (in_stack_00000018 == 0) {
              in_stack_00000018 = 0;
              in_stack_00000014 = (LPWSTR)0x0;
            }
            iVar2 = WideCharToMultiByte(in_stack_0000001c,0x220,(LPCWSTR)&stack0xffffffc4,iVar2,
                                        (LPSTR)in_stack_00000014,in_stack_00000018,(LPCSTR)0x0,
                                        (LPBOOL)0x0);
            iVar1 = iVar2;
          }
          else {
            if (in_stack_00000018 == 0) {
              ExceptionList = local_14;
              return iVar2;
            }
            if (in_stack_00000018 < iVar2) {
              ExceptionList = local_14;
              return 0;
            }
            iVar1 = LCMapStringW(in_stack_00000004,in_stack_00000008,(LPCWSTR)&stack0xffffffc4,iVar1
                                 ,in_stack_00000014,in_stack_00000018);
          }
          if (iVar1 != 0) {
            ExceptionList = local_14;
            return iVar2;
          }
        }
      }
    }
  }
  ExceptionList = local_14;
  return 0;
}
