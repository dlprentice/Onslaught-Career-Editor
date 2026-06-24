/* address: 0x00494b00 */
/* name: CMeshPart__NameMatchesWheelTokenSet */
/* signature: bool __cdecl CMeshPart__NameMatchesWheelTokenSet(int param_1) */


bool __cdecl CMeshPart__NameMatchesWheelTokenSet(int param_1)

{
  char *a;
  int iVar1;

  a = (char *)(param_1 + 0xdc);
  iVar1 = stricmp(a,&DAT_0062dcbc);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,&DAT_0062dcb4,(void *)0x4);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,s_Wheel_0062dcac,(void *)0x5);
  return iVar1 != 0;
}
