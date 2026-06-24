/* address: 0x0056a69e */
/* name: CRT__GetStringTypeACompat */
/* signature: int CRT__GetStringTypeACompat(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__GetStringTypeACompat(void)

{
  undefined1 *puVar1;
  BOOL BVar2;
  int iVar3;
  DWORD in_stack_00000004;
  LPCSTR in_stack_00000008;
  int in_stack_0000000c;
  LPWORD in_stack_00000010;
  UINT in_stack_00000014;
  LCID in_stack_00000018;
  int in_stack_0000001c;
  WORD local_20 [2];
  undefined1 *local_1c;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e6190;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  local_1c = &stack0xffffffc8;
  iVar3 = DAT_009d0ad0;
  ExceptionList = &local_14;
  puVar1 = &stack0xffffffc8;
  if (DAT_009d0ad0 == 0) {
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
  DAT_009d0ad0 = iVar3;
  if (DAT_009d0ad0 != 2) {
    if (DAT_009d0ad0 == 1) {
      if (in_stack_00000014 == 0) {
        in_stack_00000014 = DAT_009d09a8;
      }
      iVar3 = MultiByteToWideChar(in_stack_00000014,(-(uint)(in_stack_0000001c != 0) & 8) + 1,
                                  in_stack_00000008,in_stack_0000000c,(LPWSTR)0x0,0);
      if (iVar3 != 0) {
        local_8 = 0;
        CDXTexture__Helper_0055def0();
        local_1c = &stack0xffffffc8;
        _memset(&stack0xffffffc8,0,iVar3 * 2);
        local_8 = 0xffffffff;
        if ((&stack0x00000000 != (undefined1 *)0x38) &&
           (iVar3 = MultiByteToWideChar(in_stack_00000014,1,in_stack_00000008,in_stack_0000000c,
                                        (LPWSTR)&stack0xffffffc8,iVar3), iVar3 != 0)) {
          BVar2 = GetStringTypeW(in_stack_00000004,(LPCWSTR)&stack0xffffffc8,iVar3,in_stack_00000010
                                );
          ExceptionList = local_14;
          return BVar2;
        }
      }
    }
    ExceptionList = local_14;
    return 0;
  }
  if (in_stack_00000018 == 0) {
    in_stack_00000018 = DAT_009d0998;
  }
  BVar2 = GetStringTypeA(in_stack_00000018,in_stack_00000004,in_stack_00000008,in_stack_0000000c,
                         in_stack_00000010);
  ExceptionList = local_14;
  return BVar2;
}
