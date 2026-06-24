/* address: 0x004aa410 */
/* name: CMesh__FindTextureByNameSuffixHint */
/* signature: int * __cdecl CMesh__FindTextureByNameSuffixHint(void * param_1) */


int * __cdecl CMesh__FindTextureByNameSuffixHint(void *param_1)

{
  char *pcVar1;
  char cVar2;
  int *piVar3;
  int iVar4;
  char *pcVar5;
  char local_100 [256];

  iVar4 = -1;
  pcVar1 = (char *)((int)param_1 + 8);
  pcVar5 = pcVar1;
  do {
    if (iVar4 == 0) break;
    iVar4 = iVar4 + -1;
    cVar2 = *pcVar5;
    pcVar5 = pcVar5 + 1;
  } while (cVar2 != '\0');
  if (iVar4 == -2) {
    sprintf(local_100,s_Warning__Mesh_contains_a_null_te_0062fc50);
    DebugTrace(local_100);
    return (int *)0x0;
  }
  iVar4 = CMCBuggy__Helper_0056e170(pcVar1,&DAT_0062fc04,(void *)0x2);
  if (iVar4 == 0) {
    piVar3 = CTexture__FindTexture(param_1,4,0,-1,1,1);
    return piVar3;
  }
  iVar4 = CMCBuggy__Helper_0056e170(pcVar1,&DAT_0062fc00,(void *)0x2);
  if (iVar4 == 0) {
    piVar3 = CTexture__FindTexture(param_1,2,0,-1,1,1);
    return piVar3;
  }
  piVar3 = CTexture__FindTexture(param_1,1,0,-1,1,1);
  return piVar3;
}
