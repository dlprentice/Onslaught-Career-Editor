/* address: 0x0056e271 */
/* name: CRT__GetEnvVarValuePointerCaseInsensitive_0056e271 */
/* signature: int __cdecl CRT__GetEnvVarValuePointerCaseInsensitive_0056e271(void * param_1) */


int __cdecl CRT__GetEnvVarValuePointerCaseInsensitive_0056e271(void *param_1)

{
  int iVar1;
  size_t _MaxCount;
  size_t sVar2;
  int *piVar3;

  if (((DAT_009d4604 != 0) &&
      ((DAT_009d08dc != (int *)0x0 ||
       (((DAT_009d08e4 != 0 && (iVar1 = CRT__ProcessWideArgvTableToMultibyte(), iVar1 == 0)) &&
        (DAT_009d08dc != (int *)0x0)))))) && (piVar3 = DAT_009d08dc, param_1 != (void *)0x0)) {
    _MaxCount = _strlen(param_1);
    for (; (char *)*piVar3 != (char *)0x0; piVar3 = piVar3 + 1) {
      sVar2 = _strlen((char *)*piVar3);
      if (((_MaxCount < sVar2) && (((uchar *)*piVar3)[_MaxCount] == '=')) &&
         (iVar1 = __mbsnbicoll((uchar *)*piVar3,param_1,_MaxCount), iVar1 == 0)) {
        return *piVar3 + 1 + _MaxCount;
      }
    }
  }
  return 0;
}
