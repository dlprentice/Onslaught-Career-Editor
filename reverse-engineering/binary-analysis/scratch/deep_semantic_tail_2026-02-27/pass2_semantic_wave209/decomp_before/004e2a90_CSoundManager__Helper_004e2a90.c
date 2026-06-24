/* address: 0x004e2a90 */
/* name: CSoundManager__Helper_004e2a90 */
/* signature: char * __cdecl CSoundManager__Helper_004e2a90(void * param_1, int param_2) */


char * __cdecl CSoundManager__Helper_004e2a90(void *param_1,int param_2)

{
  char *pcVar1;
  char cVar2;
  bool bVar3;
  char *pcVar4;
  int iVar5;
  char local_100 [256];

  if (DAT_0089698c != '\0') {
    bVar3 = false;
    pcVar4 = local_100;
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      if (cVar2 == '\\') {
        if (!bVar3) {
          *pcVar4 = '\\';
          pcVar4 = pcVar4 + 1;
          bVar3 = true;
        }
      }
      else {
        *pcVar4 = cVar2;
        pcVar4 = pcVar4 + 1;
        bVar3 = false;
      }
      pcVar1 = (char *)((int)param_1 + 1);
      param_1 = (void *)((int)param_1 + 1);
      cVar2 = *pcVar1;
    }
    *pcVar4 = '\0';
    for (pcVar4 = g_pSoundDefinitionListHead; pcVar4 != (char *)0x0;
        pcVar4 = *(char **)(pcVar4 + 0xd8)) {
      iVar5 = stricmp(pcVar4,local_100);
      if (iVar5 == 0) {
        if (param_2 == 0) {
          return pcVar4;
        }
        param_2 = param_2 + -1;
      }
    }
  }
  return (char *)0x0;
}
