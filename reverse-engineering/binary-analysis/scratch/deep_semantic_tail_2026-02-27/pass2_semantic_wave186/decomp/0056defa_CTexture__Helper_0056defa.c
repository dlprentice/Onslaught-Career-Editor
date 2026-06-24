/* address: 0x0056defa */
/* name: CTexture__Helper_0056defa */
/* signature: int CTexture__Helper_0056defa(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_0056defa(void)

{
  undefined1 *puVar1;
  BOOL BVar2;
  size_t _Size;
  int iVar3;
  DWORD in_stack_00000004;
  LPCWSTR in_stack_00000008;
  int in_stack_0000000c;
  LPWORD in_stack_00000010;
  UINT in_stack_00000014;
  LCID in_stack_00000018;
  WORD local_20 [2];
  undefined1 *local_1c;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e69e0;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  local_1c = &stack0xffffffc4;
  iVar3 = DAT_009d0c2c;
  ExceptionList = &local_14;
  puVar1 = &stack0xffffffc4;
  if (DAT_009d0c2c == 0) {
    ExceptionList = &local_14;
    BVar2 = GetStringTypeW(1,L"",1,local_20);
    iVar3 = 1;
    puVar1 = local_1c;
    if (BVar2 == 0) {
      BVar2 = GetStringTypeA(0,1,&DAT_00662b28,1,local_20);
      if (BVar2 == 0) {
        ExceptionList = local_14;
        return 0;
      }
      iVar3 = 2;
      puVar1 = local_1c;
    }
  }
  local_1c = puVar1;
  DAT_009d0c2c = iVar3;
  if (DAT_009d0c2c != 1) {
    if (DAT_009d0c2c == 2) {
      if (in_stack_00000014 == 0) {
        in_stack_00000014 = DAT_009d09a8;
      }
      _Size = WideCharToMultiByte(in_stack_00000014,0x220,in_stack_00000008,in_stack_0000000c,
                                  (LPSTR)0x0,0,(LPCSTR)0x0,(LPBOOL)0x0);
      if (_Size != 0) {
        local_8 = 0;
        CRT__AllocaProbe();
        local_1c = &stack0xffffffc4;
        _memset(&stack0xffffffc4,0,_Size);
        local_8 = 0xffffffff;
        if (&stack0x00000000 != (undefined1 *)0x3c) {
          iVar3 = WideCharToMultiByte(in_stack_00000014,0x220,in_stack_00000008,in_stack_0000000c,
                                      &stack0xffffffc4,_Size,(LPCSTR)0x0,(LPBOOL)0x0);
          if (iVar3 != 0) {
            local_8 = 1;
            CRT__AllocaProbe();
            local_8 = 0xffffffff;
            if (&stack0x00000000 != (undefined1 *)0x3c) {
              if (in_stack_00000018 == 0) {
                in_stack_00000018 = DAT_009d0998;
              }
              local_1c = &stack0xffffffc4;
              *(short *)(&stack0xffffffc4 + in_stack_0000000c * 2) = -1;
              local_20[in_stack_0000000c + -0xf] = 0xffff;
              BVar2 = GetStringTypeA(in_stack_00000018,in_stack_00000004,&stack0xffffffc4,_Size,
                                     (LPWORD)&stack0xffffffc4);
              if ((local_20[in_stack_0000000c + -0xf] != 0xffff) &&
                 (*(short *)(&stack0xffffffc4 + in_stack_0000000c * 2) == -1)) {
                CRT__MemMoveOverlapSafe(in_stack_00000010,&stack0xffffffc4,in_stack_0000000c * 2);
                ExceptionList = local_14;
                return BVar2;
              }
            }
          }
        }
      }
    }
    ExceptionList = local_14;
    return 0;
  }
  BVar2 = GetStringTypeW(in_stack_00000004,in_stack_00000008,in_stack_0000000c,in_stack_00000010);
  ExceptionList = local_14;
  return BVar2;
}
