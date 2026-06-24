/* address: 0x0056c80b */
/* name: CRT__IsWindowsNtPlatform */
/* signature: int CRT__IsWindowsNtPlatform(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__IsWindowsNtPlatform(void)

{
  BOOL BVar1;
  _OSVERSIONINFOA local_98;

  local_98.dwOSVersionInfoSize = 0x94;
  BVar1 = GetVersionExA(&local_98);
  if ((BVar1 != 0) && (local_98.dwPlatformId == 2)) {
    return 1;
  }
  return 0;
}
