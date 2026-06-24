/* address: 0x00560181 */
/* name: entry */
/* signature: undefined entry(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void entry(void)

{
  DWORD DVar1;
  int iVar2;
  uint uVar3;
  HMODULE pHVar4;
  undefined4 uVar5;
  _STARTUPINFOA local_60;
  undefined1 *local_1c;
  undefined4 *local_18;
  void *pvStack_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5b28;
  puStack_10 = &LAB_0056127c;
  pvStack_14 = ExceptionList;
  local_1c = &stack0xffffff88;
  ExceptionList = &pvStack_14;
  DVar1 = GetVersion();
  _DAT_009d08cc = DVar1 >> 8 & 0xff;
  _DAT_009d08c8 = DVar1 & 0xff;
  _DAT_009d08c4 = _DAT_009d08c8 * 0x100 + _DAT_009d08cc;
  _DAT_009d08c0 = DVar1 >> 0x10;
  iVar2 = CRT__InitializeHeapSubsystem(1);
  if (iVar2 == 0) {
    CDXTexture__ReportFatalAndExitProcess(0x1c);
  }
  iVar2 = CTexture__InitializeThreadLocalState();
  if (iVar2 == 0) {
    CDXTexture__ReportFatalAndExitProcess(0x10);
  }
  local_8 = 0;
  CDXTexture__Unk_005687fc();
  DAT_009d35f4 = GetCommandLineA();
  DAT_009d090c = CTexture__Helper_00569124();
  CRT__BuildArgvTable();
  CRT__BuildEnvironTable();
  CFastVB__RunStaticInitRangesWithOptionalCallback();
  local_60.dwFlags = 0;
  GetStartupInfoA(&local_60);
  iVar2 = CRT__ParseCommandLineToken();
  if ((local_60.dwFlags & 1) == 0) {
    uVar3 = 10;
  }
  else {
    uVar3 = (uint)local_60.wShowWindow;
  }
  uVar5 = 0;
  pHVar4 = GetModuleHandleA((LPCSTR)0x0);
  iVar2 = CLTShell__WinMain(pHVar4,uVar5,iVar2,uVar3);
  CFastVB__Helper_0055dda8(iVar2);
  CDXTexture__Unk_00568c4e(*(int *)*local_18,local_18);
  return;
}
