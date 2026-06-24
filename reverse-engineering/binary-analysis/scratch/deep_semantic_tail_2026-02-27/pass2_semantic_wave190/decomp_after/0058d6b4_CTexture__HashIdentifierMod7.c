/* address: 0x0058d6b4 */
/* name: CTexture__HashIdentifierMod7 */
/* signature: uint __stdcall CTexture__HashIdentifierMod7(void * param_1) */


uint CTexture__HashIdentifierMod7(void *param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;

  uVar3 = 0;
  if ((param_1 == (void *)0x0) || (cVar1 = *(char *)param_1, cVar1 == '\0')) {
    uVar3 = 0;
  }
  else {
    do {
      iVar2 = CRT__ToUpperWithLocaleLock((int)cVar1);
      uVar3 = uVar3 * 0x13 + iVar2;
      param_1 = (void *)((int)param_1 + 1);
      cVar1 = *(char *)param_1;
    } while (cVar1 != '\0');
    uVar3 = uVar3 % 7;
  }
  return uVar3;
}
