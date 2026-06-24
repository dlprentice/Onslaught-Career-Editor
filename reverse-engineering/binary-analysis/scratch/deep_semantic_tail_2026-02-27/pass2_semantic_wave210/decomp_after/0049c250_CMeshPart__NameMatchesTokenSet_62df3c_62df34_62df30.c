/* address: 0x0049c250 */
/* name: CMeshPart__NameMatchesTokenSet_62df3c_62df34_62df30 */
/* signature: bool __cdecl CMeshPart__NameMatchesTokenSet_62df3c_62df34_62df30(int param_1) */


bool __cdecl CMeshPart__NameMatchesTokenSet_62df3c_62df34_62df30(int param_1)

{
  char *a;
  int iVar1;

  a = (char *)(param_1 + 0xdc);
  iVar1 = stricmp(a,&DAT_0062dcbc);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,&PTR_DAT_0062df3c,(void *)0x3);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,&DAT_0062df34,(void *)0x4);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,&PTR_DAT_0062df30,(void *)0x3);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = stricmp(a,&DAT_0062dd20);
  return iVar1 != 0;
}
