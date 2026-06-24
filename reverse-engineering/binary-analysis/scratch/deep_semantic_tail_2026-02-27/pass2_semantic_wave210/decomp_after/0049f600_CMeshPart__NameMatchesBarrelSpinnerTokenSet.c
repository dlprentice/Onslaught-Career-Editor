/* address: 0x0049f600 */
/* name: CMeshPart__NameMatchesBarrelSpinnerTokenSet */
/* signature: bool __cdecl CMeshPart__NameMatchesBarrelSpinnerTokenSet(int param_1) */


bool __cdecl CMeshPart__NameMatchesBarrelSpinnerTokenSet(int param_1)

{
  char *a;
  int iVar1;

  a = (char *)(param_1 + 0xdc);
  iVar1 = stricmp(a,&DAT_0062e0cc);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,s_barrel_0062dd18,(void *)0x6);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = stricmp(a,s_spinner_0062e0c4);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CMCBuggy__Helper_0056e170(a,&PTR_DAT_0062e0c0,(void *)0x3);
  return iVar1 != 0;
}
