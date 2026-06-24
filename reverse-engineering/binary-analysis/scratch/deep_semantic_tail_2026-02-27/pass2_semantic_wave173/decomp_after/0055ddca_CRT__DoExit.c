/* address: 0x0055ddca */
/* name: CRT__DoExit */
/* signature: void __cdecl CRT__DoExit(uint param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CRT__DoExit(uint param_1,int param_2,int param_3)

{
  HANDLE hProcess;
  undefined4 *puVar1;
  uint uExitCode;

  CRT__Lock_0x0D();
  if (DAT_009d08fc == 1) {
    uExitCode = param_1;
    hProcess = GetCurrentProcess();
    TerminateProcess(hProcess,uExitCode);
  }
  _DAT_009d08f8 = 1;
  DAT_009d08f4 = (undefined1)param_3;
  if (param_2 == 0) {
    if ((DAT_009d4610 != (undefined4 *)0x0) &&
       (puVar1 = (undefined4 *)(DAT_009d460c - 4), DAT_009d4610 <= puVar1)) {
      do {
        if ((code *)*puVar1 != (code *)0x0) {
          (*(code *)*puVar1)();
        }
        puVar1 = puVar1 + -1;
      } while (DAT_009d4610 <= puVar1);
    }
    CRT__InvokeFunctionPointerRange(&DAT_00622b2c,&DAT_00622b38);
  }
  CRT__InvokeFunctionPointerRange(&DAT_00622b3c,&DAT_00622b44);
  if (param_3 == 0) {
    DAT_009d08fc = 1;
                    /* WARNING: Subroutine does not return */
    ExitProcess(param_1);
  }
  CRT__Unlock_0x0D();
  return;
}
