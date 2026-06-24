/* address: 0x0042da00 */
/* name: CGame__UpdateCursorCenterWithWindowScale */
/* signature: void __cdecl CGame__UpdateCursorCenterWithWindowScale(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CGame__UpdateCursorCenterWithWindowScale(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_8;

  if (g_bDevModeEnabled == 0) {
    if ((char)param_1 != '\0') {
      iVar2 = PLATFORM__GetWindowWidth();
      DAT_0089bda8 = iVar2 / 2;
      iVar2 = PLATFORM__GetWindowHeight();
      DAT_0089bda4 = iVar2 / 2;
    }
    iVar1 = DAT_0089bda8;
    iVar2 = DAT_0089bda4;
    if (DAT_0066e94d != '\0') {
      iVar3 = PLATFORM__GetWindowWidth();
      iVar3 = iVar3 >> 1;
      iVar4 = PLATFORM__GetWindowHeight();
      iVar4 = iVar4 >> 1;
      local_8 = (int)(longlong)
                     ROUND(((float)iVar3 * _DAT_005d8bec + (float)iVar1) * _DAT_005d97c4 -
                           (float)iVar1);
      iVar5 = local_8;
      local_8 = (int)(longlong)
                     ROUND(((float)iVar4 * _DAT_005d8bec + (float)iVar2) * _DAT_005d97c4 -
                           (float)iVar2);
      if ((iVar3 != iVar1) && (iVar5 == 0)) {
        iVar5 = ((iVar1 <= iVar3) - 1 & 0xfffffffe) + 1;
      }
      if ((iVar4 != iVar2) && (local_8 == 0)) {
        local_8 = ((iVar2 <= iVar4) - 1 & 0xfffffffe) + 1;
      }
      DAT_0089bda8 = iVar5 + iVar1;
      DAT_0089bda4 = local_8 + iVar2;
      DAT_0066e94d = '\0';
    }
  }
  return;
}
