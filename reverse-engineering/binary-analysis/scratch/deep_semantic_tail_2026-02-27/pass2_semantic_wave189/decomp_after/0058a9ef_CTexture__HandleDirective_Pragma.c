/* address: 0x0058a9ef */
/* name: CTexture__HandleDirective_Pragma */
/* signature: int __fastcall CTexture__HandleDirective_Pragma(int param_1) */


int __fastcall CTexture__HandleDirective_Pragma(int param_1)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  void *unaff_EDI;
  char *pcVar4;
  bool bVar5;

  iVar1 = CTexture__ReadNextLexToken
                    (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,unaff_EDI)
  ;
  if (-1 < iVar1) {
    iVar1 = *(int *)(param_1 + 0x60);
    if (iVar1 == 9) {
      iVar2 = 0xc;
      bVar5 = true;
      pcVar3 = *(char **)(param_1 + 0x68);
      pcVar4 = "pack_matrix";
      do {
        if (iVar2 == 0) break;
        iVar2 = iVar2 + -1;
        bVar5 = *pcVar3 == *pcVar4;
        pcVar3 = pcVar3 + 1;
        pcVar4 = pcVar4 + 1;
      } while (bVar5);
      if (bVar5) {
        iVar1 = CTexture__HandlePragma_PackMatrix(param_1);
        return iVar1;
      }
      iVar2 = 8;
      bVar5 = true;
      pcVar3 = *(char **)(param_1 + 0x68);
      pcVar4 = "warning";
      do {
        if (iVar2 == 0) break;
        iVar2 = iVar2 + -1;
        bVar5 = *pcVar3 == *pcVar4;
        pcVar3 = pcVar3 + 1;
        pcVar4 = pcVar4 + 1;
      } while (bVar5);
      if (bVar5) {
        iVar1 = CTexture__HandlePragma_Warning(param_1);
        return iVar1;
      }
    }
    if ((iVar1 != 0xc) && (iVar1 != 0xd)) {
      CTexture__SkipLineContinuationAndAdvance(*(void **)(param_1 + 0x54));
    }
    iVar1 = 0;
  }
  *(undefined4 *)(param_1 + 0x28) = 1;
  return iVar1;
}
