/* address: 0x0056c960 */
/* name: CTexture__Helper_0056c960 */
/* signature: int __cdecl CTexture__Helper_0056c960(void * param_1) */


int __cdecl CTexture__Helper_0056c960(void *param_1)

{
  char cVar1;
  int iVar2;

  iVar2 = 0;
  while( true ) {
    cVar1 = *(char *)param_1;
    param_1 = (void *)((int)param_1 + 1);
    if (((cVar1 < 'A') || ('Z' < cVar1)) && ((cVar1 < 'a' || ('z' < cVar1)))) break;
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}
