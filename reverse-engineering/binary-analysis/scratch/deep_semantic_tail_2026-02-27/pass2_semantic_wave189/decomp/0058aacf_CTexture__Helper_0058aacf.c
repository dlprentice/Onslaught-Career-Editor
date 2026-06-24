/* address: 0x0058aacf */
/* name: CTexture__Helper_0058aacf */
/* signature: int CTexture__Helper_0058aacf(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_0058aacf(void)

{
  byte bVar1;
  void *this;
  undefined4 *extraout_EAX;
  undefined4 *puVar2;
  int extraout_EAX_00;
  void *this_00;
  undefined4 *extraout_EAX_01;
  void *this_01;
  undefined4 *extraout_EAX_02;
  void *this_02;
  undefined4 *extraout_EAX_03;
  int extraout_EAX_04;
  char *extraout_EAX_05;
  int extraout_EAX_06;
  void *this_03;
  undefined4 *extraout_EAX_07;
  int *piVar3;
  undefined4 *extraout_EAX_08;
  void *in_ECX;
  int iVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  void *pvVar8;
  uint uVar9;
  undefined4 **ppuVar10;
  undefined4 **ppuVar11;
  byte *pbVar12;
  undefined4 *puVar13;
  void *unaff_EDI;
  int *piVar14;
  byte *pbVar15;
  char *pcVar16;
  undefined4 *puVar17;
  int iVar18;
  bool bVar19;
  undefined4 **in_stack_00000004;
  int in_stack_00000008;
  undefined4 **in_stack_0000000c;
  undefined1 local_7c [56];
  undefined1 local_44 [32];
  undefined4 **local_24;
  undefined4 **local_20;
  undefined4 **local_1c;
  undefined4 *local_18;
  int *local_14;
  int local_10;
  undefined4 *local_c;
  void *local_8;

  local_18 = (undefined4 *)0x0;
  local_c = (undefined4 *)0x0;
  if (in_stack_00000008 == 0) {
    ppuVar10 = &local_c;
    while( true ) {
      if (in_stack_0000000c == (undefined4 **)0x0) {
        *ppuVar10 = *(undefined4 **)((int)in_ECX + 0x44);
        *(undefined4 **)((int)in_ECX + 0x44) = local_c;
        return 1;
      }
      OID__AllocObject_DefaultTag_00662b2c(0x30);
      if (this == (void *)0x0) {
        puVar2 = (undefined4 *)0x0;
      }
      else {
        CTexture__NodeType8_InitFromDescriptor(this,in_stack_0000000c + 4,unaff_EDI);
        puVar2 = extraout_EAX;
      }
      *ppuVar10 = puVar2;
      if (puVar2 == (undefined4 *)0x0) break;
      in_stack_0000000c = (undefined4 **)in_stack_0000000c[3];
      ppuVar10 = (undefined4 **)(puVar2 + 3);
    }
  }
  else {
    puVar2 = *(undefined4 **)((int)in_ECX + 0x44);
    local_8 = in_ECX;
    if (puVar2 == (undefined4 *)0x0) {
      puVar2 = *(undefined4 **)((int)in_ECX + 0x54);
      if (((char *)puVar2[1] <= (char *)*puVar2) || (*(char *)*puVar2 == '(')) {
        piVar3 = (int *)((int)in_ECX + 0x60);
        local_14 = piVar3;
        iVar18 = CTexture__ReadNextLexToken
                           (puVar2,*(void **)((int)in_ECX + 0x80),(int)piVar3,unaff_EDI);
        if ((-1 < iVar18) && (*piVar3 == 1)) {
          local_20 = (undefined4 **)((int)local_8 + 0x68);
          iVar18 = 2;
          bVar19 = true;
          ppuVar10 = local_20;
          pcVar16 = "(";
          do {
            if (iVar18 == 0) break;
            iVar18 = iVar18 + -1;
            bVar19 = *(char *)ppuVar10 == *pcVar16;
            ppuVar10 = (undefined4 **)((int)ppuVar10 + 1);
            pcVar16 = pcVar16 + 1;
          } while (bVar19);
          if (bVar19) goto LAB_0058abdc;
        }
      }
    }
    else {
      local_14 = (int *)((int)in_ECX + 0x60);
      piVar3 = puVar2 + 4;
      piVar14 = local_14;
      for (iVar18 = 8; iVar18 != 0; iVar18 = iVar18 + -1) {
        *piVar14 = *piVar3;
        piVar3 = piVar3 + 1;
        piVar14 = piVar14 + 1;
      }
      if (*local_14 == 1) {
        local_20 = (undefined4 **)((int)in_ECX + 0x68);
        iVar18 = 2;
        bVar19 = true;
        ppuVar10 = local_20;
        pcVar16 = "(";
        do {
          if (iVar18 == 0) break;
          iVar18 = iVar18 + -1;
          bVar19 = *(char *)ppuVar10 == *pcVar16;
          ppuVar10 = (undefined4 **)((int)ppuVar10 + 1);
          pcVar16 = pcVar16 + 1;
        } while (bVar19);
        if (bVar19) {
          *(undefined4 *)((int)in_ECX + 0x44) = puVar2[3];
          puVar2[3] = 0;
          (**(code **)*puVar2)(1);
LAB_0058abdc:
          local_1c = (undefined4 **)0x0;
          local_24 = &local_18;
          local_10 = 1;
          pvVar8 = local_8;
          piVar3 = local_14;
          do {
            puVar2 = *(undefined4 **)((int)pvVar8 + 0x44);
            if (puVar2 == (undefined4 *)0x0) {
              iVar18 = CTexture__ReadNextLexToken
                                 (*(void **)((int)pvVar8 + 0x54),*(void **)((int)pvVar8 + 0x80),
                                  (int)piVar3,unaff_EDI);
              pvVar8 = local_8;
              if (iVar18 < 0) goto LAB_0058b179;
            }
            else {
              piVar3 = puVar2 + 4;
              piVar14 = local_14;
              for (iVar18 = 8; iVar18 != 0; iVar18 = iVar18 + -1) {
                *piVar14 = *piVar3;
                piVar3 = piVar3 + 1;
                piVar14 = piVar14 + 1;
              }
              *(undefined4 *)((int)pvVar8 + 0x44) = puVar2[3];
              puVar2[3] = 0;
              (**(code **)*puVar2)(1);
            }
            piVar3 = local_14;
            ppuVar10 = local_24;
            if (*local_14 == 0xd) {
              CTexture__Helper_0058c893
                        ((void *)((int)pvVar8 + 4),(int)in_stack_00000004,0x5eb,0x5ea5d8);
              goto LAB_0058b179;
            }
            if (*local_24 == (undefined4 *)0x0) {
              OID__AllocObject_DefaultTag_00662b2c(0x14);
              if (extraout_EAX_00 == 0) {
                puVar2 = (undefined4 *)0x0;
              }
              else {
                puVar2 = (undefined4 *)CTexture__Helper_005987f4();
              }
              *ppuVar10 = puVar2;
              if (puVar2 == (undefined4 *)0x0) goto LAB_0058b179;
              local_1c = (undefined4 **)(puVar2 + 2);
            }
            if ((((local_10 == 1) && (*piVar3 == 1)) &&
                ((*(char *)local_20 == ',' || (*(char *)local_20 == ')')))) &&
               (*(char *)((int)pvVar8 + 0x69) == '\0')) {
              local_24 = (undefined4 **)(*ppuVar10 + 3);
            }
            else {
              OID__AllocObject_DefaultTag_00662b2c(0x30);
              if (this_00 == (void *)0x0) {
                puVar2 = (undefined4 *)0x0;
              }
              else {
                CTexture__NodeType8_InitFromDescriptor(this_00,piVar3,unaff_EDI);
                puVar2 = extraout_EAX_01;
              }
              *local_1c = puVar2;
              if (puVar2 == (undefined4 *)0x0) goto LAB_0058b179;
              local_1c = (undefined4 **)(puVar2 + 3);
              pvVar8 = local_8;
              piVar3 = local_14;
            }
            if ((*piVar3 == 1) && (*(char *)((int)pvVar8 + 0x69) == '\0')) {
              cVar7 = *(char *)local_20;
              if (cVar7 == '(') {
LAB_0058ad00:
                local_10 = local_10 + 1;
              }
              else {
                if (cVar7 != ')') {
                  if (cVar7 == '[') goto LAB_0058ad00;
                  if (cVar7 != ']') {
                    if (cVar7 == '{') goto LAB_0058ad00;
                    if (cVar7 != '}') goto LAB_0058ad03;
                  }
                }
                local_10 = local_10 + -1;
              }
            }
LAB_0058ad03:
            puVar2 = local_18;
            iVar18 = in_stack_00000008;
          } while (local_10 != 0);
          do {
            if ((puVar2 == (undefined4 *)0x0) || (puVar2[2] == 0)) break;
            iVar18 = *(int *)(iVar18 + 0xc);
            puVar2 = (undefined4 *)puVar2[3];
          } while (iVar18 != 0);
          if ((iVar18 == 0) && (puVar2 == (undefined4 *)0x0)) {
            in_stack_00000004 = &local_c;
            local_14 = (int *)0x0;
            local_10 = 0;
            local_20 = (undefined4 **)0x0;
            for (local_24 = in_stack_0000000c; local_24 != (undefined4 **)0x0;
                local_24 = (undefined4 **)local_24[3]) {
              ppuVar10 = local_24 + 4;
              local_1c = in_stack_00000004;
              if ((local_14 == (int *)0x0) && (local_10 == 0)) {
                if (*ppuVar10 != (undefined4 *)0x1) {
LAB_0058adaf:
                  if (*ppuVar10 == (undefined4 *)0x1) {
                    iVar18 = 3;
                    bVar19 = true;
                    ppuVar11 = local_24 + 6;
                    pcVar16 = "#@";
                    do {
                      if (iVar18 == 0) break;
                      iVar18 = iVar18 + -1;
                      bVar19 = *(char *)ppuVar11 == *pcVar16;
                      ppuVar11 = (undefined4 **)((int)ppuVar11 + 1);
                      pcVar16 = pcVar16 + 1;
                    } while (bVar19);
                    if (bVar19) {
                      local_10 = 1;
                      local_20 = ppuVar10;
                      goto LAB_0058afd8;
                    }
                  }
                  goto LAB_0058adcf;
                }
                iVar18 = 2;
                bVar19 = true;
                ppuVar11 = local_24 + 6;
                pcVar16 = "#";
                do {
                  if (iVar18 == 0) break;
                  iVar18 = iVar18 + -1;
                  bVar19 = *(char *)ppuVar11 == *pcVar16;
                  ppuVar11 = (undefined4 **)((int)ppuVar11 + 1);
                  pcVar16 = pcVar16 + 1;
                } while (bVar19);
                if (!bVar19) goto LAB_0058adaf;
                local_14 = (int *)0x1;
                local_20 = ppuVar10;
              }
              else {
LAB_0058adcf:
                iVar18 = in_stack_00000008;
                in_stack_0000000c = (undefined4 **)local_18;
                if (*ppuVar10 == (undefined4 *)0x9) {
                  do {
                    pbVar15 = (byte *)local_24[6];
                    pbVar12 = *(byte **)(iVar18 + 0x18);
                    do {
                      bVar1 = *pbVar12;
                      bVar19 = bVar1 < *pbVar15;
                      if (bVar1 != *pbVar15) {
LAB_0058ae09:
                        iVar4 = (1 - (uint)bVar19) - (uint)(bVar19 != 0);
                        goto LAB_0058ae0e;
                      }
                      if (bVar1 == 0) break;
                      bVar1 = pbVar12[1];
                      bVar19 = bVar1 < pbVar15[1];
                      if (bVar1 != pbVar15[1]) goto LAB_0058ae09;
                      pbVar12 = pbVar12 + 2;
                      pbVar15 = pbVar15 + 2;
                    } while (bVar1 != 0);
                    iVar4 = 0;
LAB_0058ae0e:
                    if (iVar4 == 0) break;
                    iVar18 = *(int *)(iVar18 + 0xc);
                    in_stack_0000000c = (undefined4 **)in_stack_0000000c[3];
                  } while (iVar18 != 0);
                  if (iVar18 == 0) goto LAB_0058ae65;
                  for (iVar18 = (int)in_stack_0000000c[2]; iVar18 != 0;
                      iVar18 = *(int *)(iVar18 + 0xc)) {
                    OID__AllocObject_DefaultTag_00662b2c(0x30);
                    if (this_01 == (void *)0x0) {
                      puVar2 = (undefined4 *)0x0;
                    }
                    else {
                      CTexture__NodeType8_InitFromDescriptor
                                (this_01,(void *)(iVar18 + 0x10),unaff_EDI);
                      puVar2 = extraout_EAX_02;
                    }
                    *in_stack_00000004 = puVar2;
                    if (puVar2 == (undefined4 *)0x0) goto LAB_0058b179;
                    in_stack_00000004 = (undefined4 **)(puVar2 + 3);
                  }
                }
                else {
LAB_0058ae65:
                  OID__AllocObject_DefaultTag_00662b2c(0x30);
                  if (this_02 == (void *)0x0) {
                    puVar2 = (undefined4 *)0x0;
                  }
                  else {
                    CTexture__NodeType8_InitFromDescriptor(this_02,ppuVar10,unaff_EDI);
                    puVar2 = extraout_EAX_03;
                  }
                  *in_stack_00000004 = puVar2;
                  if (puVar2 == (undefined4 *)0x0) goto LAB_0058b179;
                  in_stack_00000004 = (undefined4 **)(puVar2 + 3);
                }
                if ((local_14 != (int *)0x0) || (local_10 != 0)) {
                  iVar18 = 0;
                  iVar4 = 1;
                  for (puVar2 = *local_1c; puVar2 != (undefined4 *)0x0;
                      puVar2 = (undefined4 *)puVar2[3]) {
                    if ((iVar18 != 0) && (iVar18 != puVar2[10])) {
                      iVar4 = iVar4 + 1;
                    }
                    CTexture__Helper_0058a67b((void *)puVar2[10],puVar2[0xb],0);
                    iVar4 = iVar4 + extraout_EAX_04;
                    iVar18 = puVar2[10] + puVar2[0xb];
                  }
                  CTexture__TokenList_PushAllocatedNode_0058c107
                            (local_8,(void *)(iVar4 + 1),(int)unaff_EDI);
                  if (extraout_EAX_05 == (char *)0x0) goto LAB_0058b179;
                  iVar4 = 0;
                  in_stack_0000000c = (undefined4 **)0x1;
                  cVar7 = ((local_14 == (int *)0x0) - 1U & 0xfb) + 0x27;
                  *extraout_EAX_05 = cVar7;
                  iVar18 = (int)in_stack_0000000c;
                  for (puVar2 = *local_1c; puVar2 != (undefined4 *)0x0;
                      puVar2 = (undefined4 *)puVar2[3]) {
                    in_stack_0000000c = (undefined4 **)iVar18;
                    if ((iVar4 != 0) && (iVar4 != puVar2[10])) {
                      in_stack_0000000c = (undefined4 **)(iVar18 + 1);
                      extraout_EAX_05[iVar18] = ' ';
                    }
                    CTexture__Helper_0058a67b
                              ((void *)puVar2[10],puVar2[0xb],
                               (int)(extraout_EAX_05 + (int)in_stack_0000000c));
                    iVar18 = (int)in_stack_0000000c + extraout_EAX_06;
                    iVar4 = puVar2[0xb] + puVar2[10];
                  }
                  extraout_EAX_05[iVar18] = cVar7;
                  CTexture__TokenList_InitState_Extended_0058c37c(local_7c);
                  pvVar8 = local_8;
                  iVar18 = CMeshCollisionVolume__Helper_0058c396();
                  if ((iVar18 < 0) ||
                     (iVar18 = CTexture__ReadNextLexToken
                                         (local_7c,*(void **)((int)pvVar8 + 0x80),(int)local_44,
                                          unaff_EDI), ppuVar10 = local_1c, iVar18 < 0))
                  goto LAB_0058b155;
                  if (*local_1c != (undefined4 *)0x0) {
                    (**(code **)**local_1c)(1);
                  }
                  OID__AllocObject_DefaultTag_00662b2c(0x30);
                  if (this_03 == (void *)0x0) {
                    puVar2 = (undefined4 *)0x0;
                  }
                  else {
                    CTexture__NodeType8_InitFromDescriptor(this_03,local_44,unaff_EDI);
                    puVar2 = extraout_EAX_07;
                  }
                  *ppuVar10 = puVar2;
                  if (puVar2 == (undefined4 *)0x0) goto LAB_0058b155;
                  local_10 = 0;
                  local_14 = (int *)0x0;
                  in_stack_00000004 = (undefined4 **)(puVar2 + 3);
                  CTexture__Helper_0059877e();
                }
              }
LAB_0058afd8:
              pvVar8 = local_8;
            }
            ppuVar10 = &local_c;
            puVar2 = local_c;
            while (puVar2 != (undefined4 *)0x0) {
              puVar2 = *ppuVar10;
              local_20 = (undefined4 **)puVar2[3];
              if (local_20 == (undefined4 **)0x0) {
                local_24 = (undefined4 **)0x0;
              }
              else {
                local_24 = (undefined4 **)local_20[3];
              }
              piVar3 = (int *)(-(uint)(local_20 != (undefined4 **)0x0) & (uint)(local_20 + 4));
              uVar9 = -(uint)(local_24 != (undefined4 **)0x0) & (uint)(local_24 + 4);
              if (((local_20 != (undefined4 **)0x0) && (local_24 != (undefined4 **)0x0)) &&
                 (*piVar3 == 1)) {
                iVar18 = 3;
                bVar19 = true;
                piVar3 = piVar3 + 2;
                pcVar16 = "##";
                do {
                  if (iVar18 == 0) break;
                  iVar18 = iVar18 + -1;
                  bVar19 = (char)*piVar3 == *pcVar16;
                  piVar3 = (int *)((int)piVar3 + 1);
                  pcVar16 = pcVar16 + 1;
                } while (bVar19);
                if (bVar19) {
                  local_1c = (undefined4 **)(puVar2[0xb] + *(int *)(uVar9 + 0x1c));
                  CTexture__TokenList_PushAllocatedNode_0058c107(local_8,local_1c,(int)unaff_EDI);
                  if (extraout_EAX_08 == (undefined4 *)0x0) goto LAB_0058b179;
                  uVar6 = puVar2[0xb];
                  puVar13 = (undefined4 *)puVar2[10];
                  puVar17 = extraout_EAX_08;
                  for (uVar5 = uVar6 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
                    *puVar17 = *puVar13;
                    puVar13 = puVar13 + 1;
                    puVar17 = puVar17 + 1;
                  }
                  for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
                    *(undefined1 *)puVar17 = *(undefined1 *)puVar13;
                    puVar13 = (undefined4 *)((int)puVar13 + 1);
                    puVar17 = (undefined4 *)((int)puVar17 + 1);
                  }
                  uVar6 = *(uint *)(uVar9 + 0x1c);
                  puVar13 = *(undefined4 **)(uVar9 + 0x18);
                  puVar17 = (undefined4 *)(puVar2[0xb] + (int)extraout_EAX_08);
                  for (uVar5 = uVar6 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
                    *puVar17 = *puVar13;
                    puVar13 = puVar13 + 1;
                    puVar17 = puVar17 + 1;
                  }
                  for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
                    *(undefined1 *)puVar17 = *(undefined1 *)puVar13;
                    puVar13 = (undefined4 *)((int)puVar13 + 1);
                    puVar17 = (undefined4 *)((int)puVar17 + 1);
                  }
                  CTexture__TokenList_InitState_Extended_0058c37c(local_7c);
                  iVar18 = CMeshCollisionVolume__Helper_0058c396();
                  if ((iVar18 < 0) ||
                     (iVar18 = CTexture__ReadNextLexToken
                                         (local_7c,*(void **)((int)local_8 + 0x80),(int)(puVar2 + 4)
                                          ,unaff_EDI), iVar18 < 0)) goto LAB_0058b155;
                  puVar2[3] = local_24[3];
                  local_24[3] = (undefined4 *)0x0;
                  (*(code *)**local_20)(1);
                  CTexture__Helper_0059877e();
                }
              }
              ppuVar10 = (undefined4 **)(*ppuVar10 + 3);
              pvVar8 = local_8;
              puVar2 = *ppuVar10;
            }
            *ppuVar10 = *(undefined4 **)((int)pvVar8 + 0x44);
            puVar2 = (undefined4 *)0x0;
            *(undefined4 **)((int)pvVar8 + 0x44) = local_c;
            iVar18 = 1;
            goto LAB_0058b17e;
          }
          CTexture__Helper_0058c893((void *)((int)pvVar8 + 4),(int)in_stack_00000004,0x5ec,0x5ea5a4)
          ;
        }
      }
    }
  }
  goto LAB_0058b179;
LAB_0058b155:
  CTexture__Helper_0059877e();
LAB_0058b179:
  iVar18 = 0;
  puVar2 = local_c;
LAB_0058b17e:
  if (local_18 != (undefined4 *)0x0) {
    (**(code **)*local_18)(1);
  }
  if (puVar2 != (undefined4 *)0x0) {
    (**(code **)*puVar2)(1);
  }
  return iVar18;
}
