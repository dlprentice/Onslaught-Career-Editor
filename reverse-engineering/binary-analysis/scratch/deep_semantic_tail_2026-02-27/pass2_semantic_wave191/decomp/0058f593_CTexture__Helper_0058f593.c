/* address: 0x0058f593 */
/* name: CTexture__Helper_0058f593 */
/* signature: uint __fastcall CTexture__Helper_0058f593(void * param_1) */


uint __fastcall CTexture__Helper_0058f593(void *param_1)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  char *pcVar4;
  char *pcVar5;
  void *unaff_EDI;
  char *pcVar6;
  bool bVar7;

  piVar1 = (int *)((int)param_1 + 0x10);
  while( true ) {
    uVar2 = CTexture__GetNextTokenWithPreprocessor
                      (*(void **)((int)param_1 + 4),(int)piVar1,unaff_EDI);
    if ((int)uVar2 < 0) {
      *(undefined4 *)((int)param_1 + 0x4c) = 1;
      *(undefined4 *)((int)param_1 + 0x50) = 1;
      return 0xffffffff;
    }
    iVar3 = *piVar1;
    if (iVar3 < 10) break;
    if (iVar3 == 10) {
      return 0x110;
    }
    if (iVar3 != 0xc) {
      if (iVar3 != 0xd) {
        return 0x110;
      }
      return 0xffffffff;
    }
  }
  if (iVar3 != 9) {
    if (iVar3 == 0) {
      return 0x110;
    }
    if (iVar3 == 1) {
      if (*(char *)((int)param_1 + 0x19) != '\0') {
        return 0x110;
      }
      return (int)*(char *)((int)param_1 + 0x18);
    }
    if (iVar3 < 2) {
      return 0x110;
    }
    if (4 < iVar3) {
      if (8 < iVar3) {
        return 0x110;
      }
      return 0x10f;
    }
    return 0x10e;
  }
  pcVar5 = *(char **)((int)param_1 + 0x18);
  iVar3 = 0xb;
  bVar7 = true;
  pcVar4 = pcVar5;
  pcVar6 = "entrypoint";
  do {
    if (iVar3 == 0) break;
    iVar3 = iVar3 + -1;
    bVar7 = *pcVar4 == *pcVar6;
    pcVar4 = pcVar4 + 1;
    pcVar6 = pcVar6 + 1;
  } while (bVar7);
  if (bVar7) {
    uVar2 = 0x101;
  }
  else {
    iVar3 = 5;
    bVar7 = true;
    pcVar4 = pcVar5;
    pcVar6 = "true";
    do {
      if (iVar3 == 0) break;
      iVar3 = iVar3 + -1;
      bVar7 = *pcVar4 == *pcVar6;
      pcVar4 = pcVar4 + 1;
      pcVar6 = pcVar6 + 1;
    } while (bVar7);
    if (bVar7) {
      uVar2 = 0x111;
    }
    else {
      iVar3 = 6;
      bVar7 = true;
      pcVar4 = "false";
      do {
        if (iVar3 == 0) break;
        iVar3 = iVar3 + -1;
        bVar7 = *pcVar5 == *pcVar4;
        pcVar5 = pcVar5 + 1;
        pcVar4 = pcVar4 + 1;
      } while (bVar7);
      if (bVar7) {
        uVar2 = 0x112;
      }
      else if (*(int *)((int)param_1 + 0x38) == -1) {
        uVar2 = 0x10d;
      }
      else {
        uVar2 = CTexture__ParseShaderSemanticToken(param_1,(int)piVar1,unaff_EDI);
      }
    }
  }
  return uVar2;
}
