/* address: 0x0048de00 */
/* name: CTokenArchive__Helper_0048de00 */
/* signature: void __stdcall CTokenArchive__Helper_0048de00(void * param_1, int param_2) */


void CTokenArchive__Helper_0048de00(void *param_1,int param_2)

{
  char cVar1;
  uint uVar2;
  char *pcVar3;

  DXMemBuffer__ReadLine(param_1,param_2);
  uVar2 = 0xffffffff;
  pcVar3 = param_1;
  do {
    if (uVar2 == 0) break;
    uVar2 = uVar2 - 1;
    cVar1 = *pcVar3;
    pcVar3 = pcVar3 + 1;
  } while (cVar1 != '\0');
  uVar2 = ~uVar2;
  if ((uVar2 != 1) && (*(char *)((uVar2 - 2) + (int)param_1) == '\n')) {
    *(undefined1 *)((uVar2 - 2) + (int)param_1) = 0;
  }
  return;
}
