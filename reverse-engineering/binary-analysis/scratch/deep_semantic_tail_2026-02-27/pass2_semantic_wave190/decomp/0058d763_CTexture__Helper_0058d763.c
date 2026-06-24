/* address: 0x0058d763 */
/* name: CTexture__Helper_0058d763 */
/* signature: void __cdecl CTexture__Helper_0058d763(void * param_1, void * param_2) */


void __cdecl CTexture__Helper_0058d763(void *param_1,void *param_2)

{
  int *piVar1;
  int iVar2;
  char *pcVar3;
  void *unaff_EDI;
  char *pcVar4;
  bool bVar5;
  undefined1 local_1004 [255];
  undefined1 local_f05;
  undefined4 uStackY_38;

  CRT__AllocaProbe();
  iVar2 = 0xd;
  bVar5 = true;
  *(undefined4 *)((int)param_1 + 0x4c) = 1;
  pcVar3 = param_2;
  pcVar4 = "syntax error";
  do {
    if (iVar2 == 0) break;
    iVar2 = iVar2 + -1;
    bVar5 = *pcVar3 == *pcVar4;
    pcVar3 = pcVar3 + 1;
    pcVar4 = pcVar4 + 1;
  } while (bVar5);
  if (bVar5) {
    piVar1 = (int *)((int)param_1 + 0x10);
    CTexture__LogUnexpectedTokenError_0058cabd
              (*(void **)param_1,(void *)0x7d0,(int)piVar1,unaff_EDI);
    if (*piVar1 == 9) {
      if (*(int *)((int)param_1 + 0x54) == 0x7e7) {
        CTexture__Helper_0058c893(*(void **)param_1,(int)piVar1,0x7e7,0x5ec984);
      }
      if (*(int *)((int)param_1 + 0x54) == 0x7e8) {
        CTexture__Helper_0058c893(*(void **)param_1,(int)piVar1,0x7e8,0x5ec960);
      }
    }
  }
  else {
    CRT__VsnprintfAndTerminate_005d070f(local_1004,0x1000,param_2,&stack0x0000000c);
    local_f05 = 0;
    uStackY_38 = 0x58d819;
    CTexture__Helper_0058c893(*(void **)param_1,(int)param_1 + 0x10,0,0x5ea38c);
  }
  return;
}
