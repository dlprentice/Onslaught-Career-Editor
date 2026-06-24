/* address: 0x005d0c7f */
/* name: CRT__LCMapStringW_AnsiCompat */
/* signature: int CRT__LCMapStringW_AnsiCompat(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__LCMapStringW_AnsiCompat(void)

{
  int iVar1;
  int iVar2;
  size_t cchDest;
  LCID in_stack_00000004;
  uint in_stack_00000008;
  LPCWSTR in_stack_0000000c;
  int in_stack_00000010;
  LPWSTR in_stack_00000014;
  size_t in_stack_00000018;
  UINT in_stack_0000001c;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_0060c180;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  ExceptionList = &local_14;
  if (DAT_009d304c == 0) {
    ExceptionList = &local_14;
    iVar1 = LCMapStringW(0,0x100,L"",1,(LPWSTR)0x0,0);
    if (iVar1 == 0) {
      iVar1 = LCMapStringA(0,0x100,&DAT_00662b28,1,(LPSTR)0x0,0);
      if (iVar1 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      DAT_009d304c = 2;
    }
    else {
      DAT_009d304c = 1;
    }
  }
  if (0 < in_stack_00000010) {
    in_stack_00000010 = CRT__WcsNLen(in_stack_0000000c,in_stack_00000010);
  }
  if (DAT_009d304c == 1) {
    iVar1 = LCMapStringW(in_stack_00000004,in_stack_00000008,in_stack_0000000c,in_stack_00000010,
                         in_stack_00000014,in_stack_00000018);
    ExceptionList = local_14;
    return iVar1;
  }
  if (DAT_009d304c == 2) {
    if (in_stack_0000001c == 0) {
      in_stack_0000001c = DAT_009d09a8;
    }
    iVar1 = WideCharToMultiByte(in_stack_0000001c,0x220,in_stack_0000000c,in_stack_00000010,
                                (LPSTR)0x0,0,(LPCSTR)0x0,(LPBOOL)0x0);
    if (iVar1 != 0) {
      local_8 = 0;
      CRT__AllocaProbe();
      local_8 = 0xffffffff;
      if ((&stack0x00000000 != (undefined1 *)0x3c) &&
         (iVar2 = WideCharToMultiByte(in_stack_0000001c,0x220,in_stack_0000000c,in_stack_00000010,
                                      &stack0xffffffc4,iVar1,(LPCSTR)0x0,(LPBOOL)0x0), iVar2 != 0))
      {
        cchDest = LCMapStringA(in_stack_00000004,in_stack_00000008,&stack0xffffffc4,iVar1,(LPSTR)0x0
                               ,0);
        if (cchDest != 0) {
          local_8 = 1;
          CRT__AllocaProbe();
          local_8 = 0xffffffff;
          if ((&stack0x00000000 != (undefined1 *)0x3c) &&
             (iVar1 = LCMapStringA(in_stack_00000004,in_stack_00000008,&stack0xffffffc4,iVar1,
                                   &stack0xffffffc4,cchDest), iVar1 != 0)) {
            if ((in_stack_00000008 & 0x400) != 0) {
              if (in_stack_00000018 != 0) {
                if ((int)cchDest <= (int)in_stack_00000018) {
                  in_stack_00000018 = cchDest;
                }
                _strncpy((char *)in_stack_00000014,&stack0xffffffc4,in_stack_00000018);
                ExceptionList = local_14;
                return cchDest;
              }
              ExceptionList = local_14;
              return cchDest;
            }
            if (in_stack_00000018 == 0) {
              in_stack_00000018 = 0;
              in_stack_00000014 = (LPWSTR)0x0;
            }
            iVar1 = MultiByteToWideChar(in_stack_0000001c,1,&stack0xffffffc4,cchDest,
                                        in_stack_00000014,in_stack_00000018);
            if (iVar1 != 0) {
              ExceptionList = local_14;
              return iVar1;
            }
          }
        }
      }
    }
  }
  ExceptionList = local_14;
  return 0;
}
