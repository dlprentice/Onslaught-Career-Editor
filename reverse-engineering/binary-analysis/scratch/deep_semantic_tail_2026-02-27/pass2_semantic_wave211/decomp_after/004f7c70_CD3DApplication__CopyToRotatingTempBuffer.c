/* address: 0x004f7c70 */
/* name: CD3DApplication__CopyToRotatingTempBuffer */
/* signature: int __cdecl CD3DApplication__CopyToRotatingTempBuffer(void * param_1) */


int __cdecl CD3DApplication__CopyToRotatingTempBuffer(void *param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;

  uVar4 = 0xffffffff;
  pcVar7 = param_1;
  do {
    if (uVar4 == 0) break;
    uVar4 = uVar4 - 1;
    cVar1 = *pcVar7;
    pcVar7 = pcVar7 + 1;
  } while (cVar1 != '\0');
  iVar5 = ~uVar4 - 1;
  DAT_00854d44 = DAT_00854d44 + 1;
  if (3 < DAT_00854d44) {
    DAT_00854d44 = 0;
  }
  iVar2 = DAT_00854d44;
  iVar3 = 0;
  if (0 < iVar5) {
    iVar6 = DAT_00854d44 * 0x1000;
    do {
      (&DAT_00848d40)[iVar3 + iVar6] = *(undefined1 *)(iVar3 + (int)param_1);
      iVar3 = iVar3 + 1;
    } while (iVar3 < iVar5);
  }
  (&DAT_00848d40)[iVar5 + iVar2 * 0x1000] = 0;
  return (int)(&DAT_00848d40 + iVar2 * 0x1000);
}
