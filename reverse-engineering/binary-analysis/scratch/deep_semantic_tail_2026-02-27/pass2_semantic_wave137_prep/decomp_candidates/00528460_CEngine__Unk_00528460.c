/* address: 0x00528460 */
/* name: CEngine__Unk_00528460 */
/* signature: void CEngine__Unk_00528460(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_00528460(void)

{
  int iVar1;
  undefined4 *puVar2;
  DWORD local_4;

  if (DAT_0089bec8 != (int *)0x0) {
    SetEvent(DAT_0089bebc);
    do {
      Sleep(10);
      GetExitCodeThread(DAT_0089beb4,&local_4);
    } while (local_4 == 0x103);
    DAT_0089beb4 = (HANDLE)0x0;
    (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
    (**(code **)(*DAT_0089bec8 + 8))(DAT_0089bec8);
    DAT_0089bec8 = (int *)0x0;
    CloseHandle(DAT_0089bec4);
    CloseHandle(DAT_0089bec0);
    CloseHandle(DAT_0089bebc);
    CloseHandle(DAT_0089beb8);
    DAT_0089bec4 = (HANDLE)0x0;
    DAT_0089bec0 = (HANDLE)0x0;
    DAT_0089bebc = (HANDLE)0x0;
    DAT_0089beb8 = (HANDLE)0x0;
    if (DAT_0089bfd4 != (undefined4 *)0x0) {
      (**(code **)*DAT_0089bfd4)(1);
    }
    DAT_0089bfd4 = (undefined4 *)0x0;
    puVar2 = &DAT_0089bed4;
    for (iVar1 = 0x40; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar2 = 0;
      puVar2 = puVar2 + 1;
    }
    DAT_0089bed0 = 0;
  }
  return;
}
