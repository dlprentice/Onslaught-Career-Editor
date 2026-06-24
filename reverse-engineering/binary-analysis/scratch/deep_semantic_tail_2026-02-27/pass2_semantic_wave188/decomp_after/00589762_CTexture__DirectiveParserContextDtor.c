/* address: 0x00589762 */
/* name: CTexture__DirectiveParserContextDtor */
/* signature: void __fastcall CTexture__DirectiveParserContextDtor(int param_1) */


void __fastcall CTexture__DirectiveParserContextDtor(int param_1)

{
  char *pcVar1;
  int iVar2;
  int unaff_ESI;
  char *pcVar3;
  char *pcVar4;
  bool bVar5;

  if (*(undefined4 **)(param_1 + 0x40) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x40))(1);
  }
  if (*(undefined4 **)(param_1 + 0x44) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x44))(1);
  }
  if (*(void **)(param_1 + 0x48) != (void *)0x0) {
    CTexture__IncludeFileChainDtor(*(void **)(param_1 + 0x48),(void *)0x1,unaff_ESI);
  }
  if (*(void **)(param_1 + 0x50) != (void *)0x0) {
    CTexture__IncludeContextDtor(*(void **)(param_1 + 0x50),(void *)0x1,unaff_ESI);
  }
  if (*(void **)(param_1 + 0x4c) != (void *)0x0) {
    CTexture__IncludeNodeDtor(*(void **)(param_1 + 0x4c),(void *)0x1,unaff_ESI);
  }
  pcVar1 = *(char **)(param_1 + 0x84);
  if (pcVar1 != (char *)0x0) {
    iVar2 = 2;
    bVar5 = true;
    pcVar3 = pcVar1;
    pcVar4 = "C";
    do {
      if (iVar2 == 0) break;
      iVar2 = iVar2 + -1;
      bVar5 = *pcVar3 == *pcVar4;
      pcVar3 = pcVar3 + 1;
      pcVar4 = pcVar4 + 1;
    } while (bVar5);
    if (!bVar5) {
      CRT__SetLocale(4,pcVar1);
    }
  }
  if (*(int *)(param_1 + 0x84) != 0) {
    CRT__FreeBase(*(int *)(param_1 + 0x84));
  }
  CRT__ControlFpMasked_0056947e(*(uint *)(param_1 + 0x88),0x30000);
  CTexture__TokenList_ClearAndFreeBuffers_0058c149((void *)(param_1 + 4));
  CTexture__TokenList_FreeChain_0058c0ea((void *)param_1);
  return;
}
