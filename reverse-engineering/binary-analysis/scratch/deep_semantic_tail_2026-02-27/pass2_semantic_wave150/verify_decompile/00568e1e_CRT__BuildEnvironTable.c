/* address: 0x00568e1e */
/* name: CRT__BuildEnvironTable */
/* signature: void CRT__BuildEnvironTable(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__BuildEnvironTable(void)

{
  char cVar1;
  size_t sVar2;
  undefined4 *puVar3;
  void *pvVar4;
  int iVar5;
  char *pcVar6;

  if (DAT_009d4608 == 0) {
    CDXTexture__Helper_0056836a();
  }
  iVar5 = 0;
  for (pcVar6 = DAT_009d090c; *pcVar6 != '\0'; pcVar6 = pcVar6 + sVar2 + 1) {
    if (*pcVar6 != '=') {
      iVar5 = iVar5 + 1;
    }
    sVar2 = _strlen(pcVar6);
  }
  puVar3 = _malloc(iVar5 * 4 + 4);
  DAT_009d08dc = puVar3;
  if (puVar3 == (undefined4 *)0x0) {
    __amsg_exit(9);
  }
  cVar1 = *DAT_009d090c;
  pcVar6 = DAT_009d090c;
  while (cVar1 != '\0') {
    sVar2 = _strlen(pcVar6);
    if (*pcVar6 != '=') {
      pvVar4 = _malloc(sVar2 + 1);
      *puVar3 = pvVar4;
      if (pvVar4 == (void *)0x0) {
        __amsg_exit(9);
      }
      CDXTexture__Helper_00567de0((void *)*puVar3,pcVar6);
      puVar3 = puVar3 + 1;
    }
    pcVar6 = pcVar6 + sVar2 + 1;
    cVar1 = *pcVar6;
  }
  CRT__FreeBase((int)DAT_009d090c);
  DAT_009d090c = (char *)0x0;
  *puVar3 = 0;
  DAT_009d4604 = 1;
  return;
}
