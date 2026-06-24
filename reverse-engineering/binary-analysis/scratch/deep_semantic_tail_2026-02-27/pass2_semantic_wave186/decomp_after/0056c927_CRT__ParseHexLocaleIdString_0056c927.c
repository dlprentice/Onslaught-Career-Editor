/* address: 0x0056c927 */
/* name: CRT__ParseHexLocaleIdString_0056c927 */
/* signature: int __cdecl CRT__ParseHexLocaleIdString_0056c927(void * param_1) */


int __cdecl CRT__ParseHexLocaleIdString_0056c927(void *param_1)

{
  int iVar1;
  char cVar2;

  iVar1 = 0;
  while( true ) {
    cVar2 = *(char *)param_1;
    param_1 = (void *)((int)param_1 + 1);
    if (cVar2 == '\0') break;
    if ((cVar2 < 'a') || ('f' < cVar2)) {
      if (('@' < cVar2) && (cVar2 < 'G')) {
        cVar2 = cVar2 + -7;
      }
    }
    else {
      cVar2 = cVar2 + -0x27;
    }
    iVar1 = (iVar1 + 0xffffffd) * 0x10 + (int)cVar2;
  }
  return iVar1;
}
