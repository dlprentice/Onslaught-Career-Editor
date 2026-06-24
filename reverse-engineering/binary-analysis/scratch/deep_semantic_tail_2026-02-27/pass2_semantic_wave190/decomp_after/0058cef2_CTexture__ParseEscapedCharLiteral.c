/* address: 0x0058cef2 */
/* name: CTexture__ParseEscapedCharLiteral */
/* signature: int __thiscall CTexture__ParseEscapedCharLiteral(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__ParseEscapedCharLiteral(void *this,int param_1,void *param_2,void *param_3)

{
  char cVar1;
  void *pvVar2;
  void *this_00;
  uint uVar3;
  undefined3 uVar5;
  undefined3 extraout_var;
  int iVar4;
  int unaff_ESI;
  char *pcVar6;
  char *pcVar7;

  if (*(char **)((int)this + 4) <= (uint)param_1) {
    return 0;
  }
  cVar1 = *(char *)param_1;
  uVar5 = (undefined3)((uint)this >> 8);
  if ((cVar1 == '\\') && ((*(byte *)((int)this + 0x28) & 4) == 0)) {
    pcVar6 = (char *)(param_1 + 1);
    if (*(char **)((int)this + 4) <= pcVar6) {
      CTexture__AppendDiagnosticMessage(*(void **)((int)this + 0x30),(int)this + 8,0x3ef,0x5ea8a4);
      uVar5 = extraout_var;
    }
    cVar1 = *pcVar6;
    if (cVar1 == 'a') {
      *(undefined4 *)param_2 = 7;
      goto LAB_0058d07d;
    }
    if (cVar1 == 'b') {
      *(undefined4 *)param_2 = 8;
      goto LAB_0058d07d;
    }
    if (cVar1 == 'f') {
      *(undefined4 *)param_2 = 0xc;
      goto LAB_0058d07d;
    }
    if (cVar1 == 'n') {
      *(undefined4 *)param_2 = 10;
      goto LAB_0058d07d;
    }
    if (cVar1 == 'r') {
      *(undefined4 *)param_2 = 0xd;
      goto LAB_0058d07d;
    }
    if (cVar1 == 't') {
      *(undefined4 *)param_2 = 9;
      goto LAB_0058d07d;
    }
    if (cVar1 == 'v') {
      *(undefined4 *)param_2 = 0xb;
      goto LAB_0058d07d;
    }
    if (('/' < cVar1) && (cVar1 < '8')) {
      pcVar7 = *(char **)((int)this + 4);
      if ((char *)(param_1 + 4U) < *(char **)((int)this + 4)) {
        pcVar7 = (char *)(param_1 + 4U);
      }
      iVar4 = 0;
      for (; ((pcVar6 < pcVar7 && (cVar1 = *pcVar6, '/' < cVar1)) && (cVar1 < '8'));
          pcVar6 = pcVar6 + 1) {
        iVar4 = cVar1 + -0x30 + iVar4 * 8;
      }
      *(int *)param_2 = iVar4;
      goto LAB_0058d07d;
    }
    if ((cVar1 == 'x') && (pcVar7 = (char *)(param_1 + 2), pcVar7 < *(char **)((int)this + 4))) {
      this_00 = (void *)(int)*pcVar7;
      uVar3 = CRT__IsCharTypeMask0x80((void *)CONCAT31(uVar5,cVar1),this_00,unaff_ESI);
      if (uVar3 != 0) {
        iVar4 = 0;
        for (; pcVar7 < *(char **)((int)this + 4); pcVar7 = pcVar7 + 1) {
          pvVar2 = (void *)(int)*pcVar7;
          uVar3 = CRT__IsCharTypeMask0x80(this_00,(void *)(int)*pcVar7,unaff_ESI);
          this_00 = pvVar2;
          if (uVar3 == 0) break;
          cVar1 = *pcVar7;
          iVar4 = iVar4 * 0x10;
          if (cVar1 < 'a') {
            if (cVar1 < 'A') {
              iVar4 = iVar4 + -0x30 + (int)cVar1;
            }
            else {
              iVar4 = iVar4 + -0x37 + (int)cVar1;
            }
          }
          else {
            iVar4 = iVar4 + -0x57 + (int)cVar1;
          }
        }
        *(int *)param_2 = iVar4;
        pcVar6 = pcVar7;
        goto LAB_0058d07d;
      }
    }
    cVar1 = *pcVar6;
    pcVar6 = (char *)(param_1 + 2);
  }
  else {
    pcVar6 = (char *)(param_1 + 1);
  }
  *(int *)param_2 = (int)cVar1;
LAB_0058d07d:
  return (int)pcVar6 - param_1;
}
