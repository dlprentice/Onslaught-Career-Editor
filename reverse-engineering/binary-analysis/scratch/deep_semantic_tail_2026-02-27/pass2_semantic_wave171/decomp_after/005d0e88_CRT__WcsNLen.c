/* address: 0x005d0e88 */
/* name: CRT__WcsNLen */
/* signature: int __cdecl CRT__WcsNLen(void * param_1, int param_2) */


int __cdecl CRT__WcsNLen(void *param_1,int param_2)

{
  short *psVar1;
  int iVar2;

  iVar2 = param_2;
  for (psVar1 = param_1; (iVar2 != 0 && (iVar2 = iVar2 + -1, *psVar1 != 0)); psVar1 = psVar1 + 1) {
  }
  if (*psVar1 != 0) {
    return param_2;
  }
  return (int)psVar1 - (int)param_1 >> 1;
}
