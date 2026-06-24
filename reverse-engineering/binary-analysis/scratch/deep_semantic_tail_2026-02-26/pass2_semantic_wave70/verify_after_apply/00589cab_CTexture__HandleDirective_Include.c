/* address: 0x00589cab */
/* name: CTexture__HandleDirective_Include */
/* signature: int __fastcall CTexture__HandleDirective_Include(int param_1) */


int __fastcall CTexture__HandleDirective_Include(int param_1)

{
  int *piVar1;
  byte bVar2;
  int iVar3;
  byte *pbVar4;
  int extraout_EAX;
  void *this;
  uint uVar5;
  byte *pbVar6;
  int unaff_EBX;
  void *unaff_EDI;
  bool bVar7;
  char *pcVar8;
  CHAR local_21c [260];
  byte local_118 [260];
  LPSTR local_14;
  undefined4 local_10;
  int local_c;
  byte *local_8;

  piVar1 = (int *)(param_1 + 0x60);
  iVar3 = CTexture__Unk_0058d2ad
                    (*(void **)(param_1 + 0x54),(void *)(*(uint *)(param_1 + 0x80) | 0xc),
                     (int)piVar1,unaff_EDI);
  uVar5 = 0;
  if (iVar3 < 0) {
    return iVar3;
  }
  if (*piVar1 == 10) {
    local_c = 0;
  }
  else {
    if (*piVar1 != 0xb) {
      CTexture__Helper_00589bd6(param_1,"syntax error");
      return -0x7fffbffb;
    }
    local_c = 1;
  }
  local_8 = *(byte **)(param_1 + 0x68);
  if ((*(int *)(param_1 + 0x58) == 0) && (*(int *)(*(int *)(param_1 + 0x54) + 0x18) == 0)) {
    pcVar8 = "include interface required to support #include from resource or memory";
    iVar3 = 0x5e1;
LAB_00589d44:
    CTexture__Helper_0058c893((void *)(param_1 + 4),(int)piVar1,iVar3,(int)pcVar8);
    *(undefined4 *)(param_1 + 0x30) = 1;
    *(undefined4 *)(param_1 + 0x2c) = 1;
    return -0x7fffbffb;
  }
  iVar3 = *(int *)(param_1 + 0x50);
  if (iVar3 != 0) {
    do {
      iVar3 = *(int *)(iVar3 + 0x6c);
      uVar5 = uVar5 + 1;
    } while (iVar3 != 0);
    if (0x1f < uVar5) {
      pcVar8 = "too many nested #includes";
      iVar3 = 0x5e2;
      goto LAB_00589d44;
    }
  }
  if (*(int *)(param_1 + 0x58) == 0) {
    GetFullPathNameA((LPCSTR)local_8,0x104,(LPSTR)local_118,&local_14);
    pbVar4 = local_118;
    pbVar6 = local_8;
    do {
      bVar2 = *pbVar6;
      bVar7 = bVar2 < *pbVar4;
      if (bVar2 != *pbVar4) {
LAB_00589da6:
        iVar3 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_00589dab;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar6[1];
      bVar7 = bVar2 < pbVar4[1];
      if (bVar2 != pbVar4[1]) goto LAB_00589da6;
      pbVar6 = pbVar6 + 2;
      pbVar4 = pbVar4 + 2;
    } while (bVar2 != 0);
    iVar3 = 0;
LAB_00589dab:
    if (iVar3 != 0) {
      CTexture__Helper_005d075f(local_21c,0x104,&DAT_005ea3c4);
      GetFullPathNameA(local_21c,0x104,(LPSTR)local_118,&local_14);
    }
    local_8 = local_118;
  }
  iVar3 = *(int *)(param_1 + 0x50);
  if ((iVar3 == 0) || (*(int *)(iVar3 + 0x58) == 0)) {
    local_10 = 0;
  }
  else {
    local_10 = *(undefined4 *)(iVar3 + 100);
  }
  CFastVB__Helper_00426fd0(0x70);
  if (extraout_EAX == 0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)CTexture__Helper_00589405(extraout_EAX);
  }
  if (this != (void *)0x0) {
    local_c = CTexture__OpenIncludeSourceAndInitBuffer();
    if (-1 < local_c) {
      *(undefined4 *)((int)this + 0x6c) = *(undefined4 *)(param_1 + 0x50);
      *(void **)(param_1 + 0x50) = this;
      return 0;
    }
    *(undefined4 *)(param_1 + 0x30) = 1;
    *(undefined4 *)(param_1 + 0x2c) = 1;
    CTexture__Helper_0058948d(this,(void *)0x1,unaff_EBX);
    return local_c;
  }
  return -0x7ff8fff2;
}
