/* address: 0x0058a0c6 */
/* name: CTexture__Helper_0058a0c6 */
/* signature: int __fastcall CTexture__Helper_0058a0c6(int param_1) */


int __fastcall CTexture__Helper_0058a0c6(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  void *unaff_EBP;
  char *pcVar4;
  void *unaff_EDI;
  char *pcVar5;
  bool bVar6;
  char *local_4;

  piVar1 = (int *)(param_1 + 0x60);
  iVar2 = CTexture__ReadNextLexToken
                    (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),(int)piVar1,unaff_EBP);
  if (iVar2 < 0) goto LAB_0058a1d8;
  iVar2 = *piVar1;
  if (iVar2 == 1) {
    iVar3 = 2;
    bVar6 = true;
    pcVar4 = (char *)(param_1 + 0x68);
    pcVar5 = "(";
    do {
      if (iVar3 == 0) break;
      iVar3 = iVar3 + -1;
      bVar6 = *pcVar4 == *pcVar5;
      pcVar4 = pcVar4 + 1;
      pcVar5 = pcVar5 + 1;
    } while (bVar6);
    if (!bVar6) goto LAB_0058a1c2;
    iVar2 = CTexture__ReadNextLexToken
                      (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),(int)piVar1,unaff_EDI);
    if (iVar2 < 0) goto LAB_0058a1d8;
    if (*piVar1 == 9) {
      local_4 = *(char **)(param_1 + 0x68);
      iVar2 = CTexture__ReadNextLexToken
                        (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),(int)piVar1,unaff_EDI
                        );
      if (iVar2 < 0) goto LAB_0058a1d8;
    }
    else {
      local_4 = (char *)0x0;
    }
    iVar2 = *piVar1;
    if (iVar2 != 1) goto LAB_0058a1c2;
    iVar3 = 2;
    bVar6 = true;
    pcVar4 = (char *)(param_1 + 0x68);
    pcVar5 = ")";
    do {
      if (iVar3 == 0) break;
      iVar3 = iVar3 + -1;
      bVar6 = *pcVar4 == *pcVar5;
      pcVar4 = pcVar4 + 1;
      pcVar5 = pcVar5 + 1;
    } while (bVar6);
    if (!bVar6) goto LAB_0058a1c2;
    iVar2 = CTexture__ReadNextLexToken
                      (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),(int)piVar1,unaff_EDI);
    if (iVar2 < 0) goto LAB_0058a1d8;
    iVar2 = *piVar1;
    if ((iVar2 != 0xc) && (iVar2 != 0xd)) goto LAB_0058a1c2;
    if (local_4 == (char *)0x0) {
      *(undefined4 *)(param_1 + 0x24) = 0;
    }
    else {
      iVar3 = 10;
      bVar6 = true;
      pcVar4 = local_4;
      pcVar5 = "row_major";
      do {
        if (iVar3 == 0) break;
        iVar3 = iVar3 + -1;
        bVar6 = *pcVar4 == *pcVar5;
        pcVar4 = pcVar4 + 1;
        pcVar5 = pcVar5 + 1;
      } while (bVar6);
      if (bVar6) {
        *(undefined4 *)(param_1 + 0x24) = 0x400;
      }
      else {
        iVar3 = 0xd;
        bVar6 = true;
        pcVar4 = "column_major";
        do {
          if (iVar3 == 0) break;
          iVar3 = iVar3 + -1;
          bVar6 = *local_4 == *pcVar4;
          local_4 = local_4 + 1;
          pcVar4 = pcVar4 + 1;
        } while (bVar6);
        if (!bVar6) goto LAB_0058a1c2;
        *(undefined4 *)(param_1 + 0x24) = 0x800;
      }
    }
  }
  else {
LAB_0058a1c2:
    if ((iVar2 != 0xc) && (iVar2 != 0xd)) {
      CTexture__SkipLineContinuationAndAdvance(*(void **)(param_1 + 0x54));
    }
  }
  iVar2 = 0;
LAB_0058a1d8:
  *(undefined4 *)(param_1 + 0x28) = 1;
  return iVar2;
}
