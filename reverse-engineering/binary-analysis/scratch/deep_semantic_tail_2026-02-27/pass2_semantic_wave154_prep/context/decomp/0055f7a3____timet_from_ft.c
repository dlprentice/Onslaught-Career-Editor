/* address: 0x0055f7a3 */
/* name: ___timet_from_ft */
/* signature: undefined ___timet_from_ft(void) */


/* Library Function - Single Match
    ___timet_from_ft

   Library: Visual Studio 2003 Release */

int ___timet_from_ft(FILETIME *param_1)

{
  BOOL BVar1;
  int iVar2;
  _SYSTEMTIME local_1c;
  _FILETIME local_c;

  if ((param_1->dwLowDateTime != 0) || (param_1->dwHighDateTime != 0)) {
    BVar1 = FileTimeToLocalFileTime(param_1,&local_c);
    if (BVar1 != 0) {
      BVar1 = FileTimeToSystemTime(&local_c,&local_1c);
      if (BVar1 != 0) {
        iVar2 = CTexture__Unk_00567ed0();
        return iVar2;
      }
    }
  }
  return -1;
}
