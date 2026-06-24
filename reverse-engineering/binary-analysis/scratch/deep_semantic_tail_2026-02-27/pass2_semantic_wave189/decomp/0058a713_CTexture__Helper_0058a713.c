/* address: 0x0058a713 */
/* name: CTexture__Helper_0058a713 */
/* signature: int __thiscall CTexture__Helper_0058a713(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Helper_0058a713(void *this,int param_1,void *param_2,void *param_3)

{
  int *piVar1;
  byte bVar2;
  undefined4 *puVar3;
  int *extraout_EAX;
  int iVar4;
  void *this_00;
  int extraout_EAX_00;
  int *piVar5;
  void *this_01;
  int extraout_EAX_01;
  int iVar6;
  byte *pbVar7;
  char *pcVar8;
  int *piVar9;
  void *unaff_EDI;
  byte *pbVar10;
  char *pcVar11;
  int *piVar12;
  bool bVar13;

  OID__AllocObject_DefaultTag_00662b2c(0x10);
  if (extraout_EAX == (int *)0x0) {
    param_1 = 0;
  }
  else {
    *extraout_EAX = param_1;
    extraout_EAX[1] = 0;
    extraout_EAX[2] = 0;
    extraout_EAX[3] = 0;
    param_1 = (int)extraout_EAX;
  }
  if (param_1 != 0) {
    if (param_2 != (void *)0x0) {
      puVar3 = *(undefined4 **)((int)this + 0x54);
      if (((char *)*puVar3 < (char *)puVar3[1]) && (*(char *)*puVar3 == '(')) {
        piVar5 = (int *)((int)this + 0x60);
        iVar4 = CTexture__ReadNextLexToken
                          (puVar3,*(void **)((int)this + 0x80),(int)piVar5,unaff_EDI);
        param_2 = (int *)(param_1 + 4);
        if (iVar4 < 0) goto LAB_0058a968;
        do {
          iVar4 = CTexture__ReadNextLexToken
                            (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),(int)piVar5,
                             unaff_EDI);
          if (iVar4 < 0) goto LAB_0058a968;
          if (*piVar5 != 9) goto LAB_0058a883;
          for (iVar4 = *(int *)(param_1 + 4); iVar4 != 0; iVar4 = *(int *)(iVar4 + 0xc)) {
            pbVar7 = *(byte **)(iVar4 + 0x18);
            pbVar10 = *(byte **)((int)this + 0x68);
            do {
              bVar2 = *pbVar10;
              bVar13 = bVar2 < *pbVar7;
              if (bVar2 != *pbVar7) {
LAB_0058a7e6:
                iVar6 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
                goto LAB_0058a7eb;
              }
              if (bVar2 == 0) break;
              bVar2 = pbVar10[1];
              bVar13 = bVar2 < pbVar7[1];
              if (bVar2 != pbVar7[1]) goto LAB_0058a7e6;
              pbVar10 = pbVar10 + 2;
              pbVar7 = pbVar7 + 2;
            } while (bVar2 != 0);
            iVar6 = 0;
LAB_0058a7eb:
            if (iVar6 == 0) {
              CTexture__Helper_0058c893((void *)((int)this + 4),(int)piVar5,0x5e7,0x5ea52c);
              break;
            }
          }
          OID__AllocObject_DefaultTag_00662b2c(0x30);
          if (this_00 == (void *)0x0) {
            iVar4 = 0;
          }
          else {
            CTexture__NodeType8_InitFromDescriptor(this_00,piVar5,unaff_EDI);
            iVar4 = extraout_EAX_00;
          }
          *(int *)param_2 = iVar4;
          if (iVar4 == 0) goto LAB_0058a942;
          param_2 = (void *)(iVar4 + 0xc);
          iVar4 = CTexture__ReadNextLexToken
                            (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),(int)piVar5,
                             unaff_EDI);
          if (iVar4 < 0) goto LAB_0058a968;
          if (*piVar5 != 1) goto LAB_0058a883;
          iVar4 = 2;
          bVar13 = true;
          pcVar8 = ",";
          pcVar11 = (char *)((int)this + 0x68);
          do {
            if (iVar4 == 0) break;
            iVar4 = iVar4 + -1;
            bVar13 = *pcVar8 == *pcVar11;
            pcVar8 = pcVar8 + 1;
            pcVar11 = pcVar11 + 1;
          } while (bVar13);
        } while (bVar13);
        iVar4 = 2;
        bVar13 = true;
        pcVar8 = ")";
        pcVar11 = (char *)((int)this + 0x68);
        do {
          if (iVar4 == 0) break;
          iVar4 = iVar4 + -1;
          bVar13 = *pcVar8 == *pcVar11;
          pcVar8 = pcVar8 + 1;
          pcVar11 = pcVar11 + 1;
        } while (bVar13);
        if (!bVar13) {
LAB_0058a883:
          if ((*piVar5 == 0xc) || (*piVar5 == 0xd)) {
            *(undefined4 *)((int)this + 0x28) = 1;
          }
          CTexture__LogUnexpectedTokenError_0058cabd
                    ((void *)((int)this + 4),(void *)0x5dc,(int)piVar5,unaff_EDI);
          *(undefined4 *)((int)this + 0x2c) = 1;
          iVar4 = -0x7fffbffb;
          goto LAB_0058a968;
        }
      }
    }
    piVar5 = (int *)(param_1 + 8);
    while( true ) {
      puVar3 = *(undefined4 **)((int)this + 0x44);
      piVar1 = (int *)((int)this + 0x60);
      if (puVar3 == (undefined4 *)0x0) {
        iVar4 = CTexture__ReadNextLexToken
                          (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),(int)piVar1,
                           unaff_EDI);
        if (iVar4 < 0) goto LAB_0058a968;
      }
      else {
        piVar9 = puVar3 + 4;
        piVar12 = piVar1;
        for (iVar4 = 8; iVar4 != 0; iVar4 = iVar4 + -1) {
          *piVar12 = *piVar9;
          piVar9 = piVar9 + 1;
          piVar12 = piVar12 + 1;
        }
        *(undefined4 *)((int)this + 0x44) = puVar3[3];
        puVar3[3] = 0;
        (**(code **)*puVar3)(1);
        *(undefined4 *)((int)this + 0x70) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x18);
        *(undefined4 *)((int)this + 0x74) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x1c);
      }
      if ((*piVar1 == 0xc) || (*piVar1 == 0xd)) {
        *(undefined4 *)((int)this + 0x28) = 1;
        iVar4 = CTexture__Helper_0058a58d((void *)param_1);
        if (-1 < iVar4) {
          param_1 = 0;
          iVar4 = 0;
        }
        goto LAB_0058a968;
      }
      OID__AllocObject_DefaultTag_00662b2c(0x30);
      if (this_01 == (void *)0x0) {
        iVar4 = 0;
      }
      else {
        CTexture__NodeType8_InitFromDescriptor(this_01,piVar1,unaff_EDI);
        iVar4 = extraout_EAX_01;
      }
      *piVar5 = iVar4;
      if (iVar4 == 0) break;
      piVar5 = (int *)(iVar4 + 0xc);
    }
  }
LAB_0058a942:
  iVar4 = -0x7ff8fff2;
LAB_0058a968:
  if (param_1 != 0) {
    CTexture__IncludeNodeDtor((void *)param_1,(void *)0x1,(int)unaff_EDI);
  }
  return iVar4;
}
