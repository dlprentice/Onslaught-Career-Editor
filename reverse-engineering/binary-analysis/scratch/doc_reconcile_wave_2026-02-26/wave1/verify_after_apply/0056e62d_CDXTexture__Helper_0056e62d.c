/* address: 0x0056e62d */
/* name: CDXTexture__Helper_0056e62d */
/* signature: int CDXTexture__Helper_0056e62d(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_0056e62d(void)

{
  undefined1 *puVar1;
  int iVar2;
  BOOL BVar3;
  BYTE *pBVar4;
  int iVar5;
  LCID in_stack_00000004;
  DWORD in_stack_00000008;
  byte *in_stack_0000000c;
  int in_stack_00000010;
  byte *in_stack_00000014;
  int in_stack_00000018;
  UINT in_stack_0000001c;
  _cpinfo local_40;
  undefined1 *local_2c;
  PCNZWCH local_28;
  int local_24;
  int local_20;
  undefined1 *local_1c;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e6a18;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  local_1c = &stack0xffffffb0;
  ExceptionList = &local_14;
  puVar1 = &stack0xffffffb0;
  if (DAT_009d0c38 == 0) {
    ExceptionList = &local_14;
    iVar2 = CompareStringW(0,0,L"",1,L"",1);
    if (iVar2 == 0) {
      iVar2 = CompareStringA(0,0,&DAT_00662b28,1,&DAT_00662b28,1);
      if (iVar2 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      DAT_009d0c38 = 2;
      puVar1 = local_1c;
    }
    else {
      DAT_009d0c38 = 1;
      puVar1 = local_1c;
    }
  }
  local_1c = puVar1;
  if (0 < in_stack_00000010) {
    in_stack_00000010 = CDXTexture__Helper_0056e8aa(in_stack_0000000c,in_stack_00000010);
  }
  if (0 < in_stack_00000018) {
    in_stack_00000018 = CDXTexture__Helper_0056e8aa(in_stack_00000014,in_stack_00000018);
  }
  if (DAT_009d0c38 == 2) {
    iVar2 = CompareStringA(in_stack_00000004,in_stack_00000008,(PCNZCH)in_stack_0000000c,
                           in_stack_00000010,(PCNZCH)in_stack_00000014,in_stack_00000018);
    ExceptionList = local_14;
    return iVar2;
  }
  if (DAT_009d0c38 == 1) {
    if (in_stack_0000001c == 0) {
      in_stack_0000001c = DAT_009d09a8;
    }
    if ((in_stack_00000010 == 0) || (in_stack_00000018 == 0)) {
      if (in_stack_00000010 == in_stack_00000018) {
        ExceptionList = local_14;
        return 2;
      }
      if (1 < in_stack_00000018) {
        ExceptionList = local_14;
        return 1;
      }
      if (1 < in_stack_00000010) {
        ExceptionList = local_14;
        return 3;
      }
      BVar3 = GetCPInfo(in_stack_0000001c,&local_40);
      if (BVar3 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      if (0 < in_stack_00000010) {
        if (local_40.MaxCharSize < 2) {
          ExceptionList = local_14;
          return 3;
        }
        pBVar4 = local_40.LeadByte;
        while( true ) {
          if (local_40.LeadByte[0] == 0) {
            ExceptionList = local_14;
            return 3;
          }
          if (pBVar4[1] == 0) break;
          if ((*pBVar4 <= *in_stack_0000000c) && (*in_stack_0000000c <= pBVar4[1])) {
            ExceptionList = local_14;
            return 2;
          }
          pBVar4 = pBVar4 + 2;
          local_40.LeadByte[0] = *pBVar4;
        }
        ExceptionList = local_14;
        return 3;
      }
      if (0 < in_stack_00000018) {
        if (local_40.MaxCharSize < 2) {
          ExceptionList = local_14;
          return 1;
        }
        pBVar4 = local_40.LeadByte;
        while( true ) {
          if (local_40.LeadByte[0] == 0) {
            ExceptionList = local_14;
            return 1;
          }
          if (pBVar4[1] == 0) break;
          if ((*pBVar4 <= *in_stack_00000014) && (*in_stack_00000014 <= pBVar4[1])) {
            ExceptionList = local_14;
            return 2;
          }
          pBVar4 = pBVar4 + 2;
          local_40.LeadByte[0] = *pBVar4;
        }
        ExceptionList = local_14;
        return 1;
      }
    }
    local_20 = MultiByteToWideChar(in_stack_0000001c,9,(LPCSTR)in_stack_0000000c,in_stack_00000010,
                                   (LPWSTR)0x0,0);
    if (local_20 != 0) {
      local_8 = 0;
      CDXTexture__Helper_0055def0();
      local_8 = 0xffffffff;
      if ((&stack0x00000000 != (undefined1 *)0x50) &&
         (local_28 = (PCNZWCH)&stack0xffffffb0, local_1c = &stack0xffffffb0,
         iVar2 = MultiByteToWideChar(in_stack_0000001c,1,(LPCSTR)in_stack_0000000c,in_stack_00000010
                                     ,(LPWSTR)&stack0xffffffb0,local_20), iVar2 != 0)) {
        iVar2 = MultiByteToWideChar(in_stack_0000001c,9,(LPCSTR)in_stack_00000014,in_stack_00000018,
                                    (LPWSTR)0x0,0);
        if (iVar2 != 0) {
          local_8 = 1;
          local_24 = iVar2;
          CDXTexture__Helper_0055def0();
          local_8 = 0xffffffff;
          if ((&stack0x00000000 != (undefined1 *)0x50) &&
             (local_2c = &stack0xffffffb0, local_1c = &stack0xffffffb0,
             iVar5 = MultiByteToWideChar(in_stack_0000001c,1,(LPCSTR)in_stack_00000014,
                                         in_stack_00000018,(LPWSTR)&stack0xffffffb0,iVar2),
             iVar5 != 0)) {
            iVar2 = CompareStringW(in_stack_00000004,in_stack_00000008,local_28,local_20,
                                   (PCNZWCH)&stack0xffffffb0,iVar2);
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
