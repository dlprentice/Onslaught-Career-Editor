/* address: 0x00476fe0 */
/* name: CVBufTexture__Helper_00476fe0 */
/* signature: void CVBufTexture__Helper_00476fe0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CVBufTexture__Helper_00476fe0(void)

{
  uint uVar1;
  bool bVar2;
  char cVar3;
  undefined4 *puVar4;
  void *pvVar5;
  float *extraout_EAX;
  void *extraout_EAX_00;
  undefined4 extraout_EAX_01;
  undefined1 *puVar6;
  undefined1 *puVar7;
  int extraout_EAX_02;
  int *piVar8;
  int iVar9;
  int *piVar10;
  int iVar11;
  int *this;
  float *pfVar12;
  float fVar13;
  float unaff_EBX;
  float unaff_EBP;
  undefined1 *puVar14;
  float fVar15;
  float unaff_ESI;
  undefined4 *puVar16;
  float fVar17;
  undefined4 *puVar18;
  float fVar19;
  float10 extraout_ST0;
  float10 fVar20;
  undefined4 uVar21;
  float *pfVar22;
  undefined1 *puVar23;
  float *pfVar24;
  undefined1 *puVar25;
  float *pfVar26;
  undefined1 *puVar27;
  undefined1 *puVar28;
  undefined1 *puVar29;
  float fVar30;
  float fStack_290;
  undefined1 *puStack_288;
  float *pfStack_284;
  float fVar31;
  undefined1 auStack_26c [4];
  float fStack_268;
  float fStack_264;
  int iStack_258;
  float fStack_254;
  float fStack_250;
  void *pvStack_24c;
  float fStack_248;
  float fStack_244;
  float fStack_240;
  int iStack_23c;
  int iStack_228;
  float fStack_224;
  float fStack_220;
  int iStack_21c;
  float fStack_218;
  float fStack_214;
  float fStack_210;
  float fStack_20c;
  float fStack_208;
  float fStack_1fc;
  int iStack_1f8;
  float fStack_1f4;
  float fStack_1f0;
  float fStack_1ec;
  float fStack_1e8;
  float local_1e4 [7];
  undefined1 auStack_1c8 [12];
  float fStack_1bc;
  undefined4 uStack_1b8;
  float fStack_1b4;
  undefined4 uStack_1b0;
  undefined1 auStack_1ac [4];
  int iStack_1a8;
  int iStack_1a4;
  undefined4 uStack_190;
  undefined1 auStack_18c [4];
  undefined1 auStack_188 [4];
  undefined1 auStack_184 [12];
  undefined1 auStack_178 [4];
  float afStack_174 [2];
  undefined1 auStack_16c [4];
  undefined1 auStack_168 [12];
  undefined1 auStack_15c [76];
  undefined4 auStack_110 [13];
  undefined1 auStack_dc [12];
  undefined4 auStack_d0 [16];
  undefined4 auStack_90 [13];
  undefined1 auStack_5c [12];
  undefined1 auStack_50 [44];
  char cStack_24;
  char cStack_20;
  char cStack_1c;

  pfStack_284 = local_1e4;
  puStack_288 = (undefined1 *)0x477006;
  (*(code *)**(undefined4 **)(&DAT_0089c9a4)[DAT_0089ce4c])();
  puStack_288 = auStack_184;
  puVar4 = (undefined4 *)(**(code **)(*(int *)(&DAT_0089c9a4)[DAT_0089ce4c] + 4))();
  uStack_1b0 = puVar4[8];
  fStack_1b4 = (float)puVar4[4];
  uStack_1b8 = *puVar4;
  (**(code **)(*(int *)(&DAT_0089c9a4)[DAT_0089ce4c] + 4))(auStack_188);
  (**(code **)(*(int *)(&DAT_0089c9a4)[DAT_0089ce4c] + 4))();
  puVar4 = auStack_90;
  puVar16 = &DAT_0089ce14;
  puVar18 = &uStack_190;
  for (iVar11 = 6; iVar11 != 0; iVar11 = iVar11 + -1) {
    *puVar18 = *puVar16;
    puVar16 = puVar16 + 1;
    puVar18 = puVar18 + 1;
  }
  puVar7 = auStack_50;
  puVar16 = &DAT_009c6994;
  puVar18 = auStack_d0;
  for (iVar11 = 0x10; iVar11 != 0; iVar11 = iVar11 + -1) {
    *puVar18 = *puVar16;
    puVar16 = puVar16 + 1;
    puVar18 = puVar18 + 1;
  }
  puVar16 = &DAT_009c6914;
  puVar18 = auStack_110;
  for (iVar11 = 0x10; iVar11 != 0; iVar11 = iVar11 + -1) {
    *puVar18 = *puVar16;
    puVar16 = puVar16 + 1;
    puVar18 = puVar18 + 1;
  }
  puVar16 = &DAT_009c6954;
  puVar18 = auStack_90;
  for (iVar11 = 0x10; iVar11 != 0; iVar11 = iVar11 + -1) {
    *puVar18 = *puVar16;
    puVar16 = puVar16 + 1;
    puVar18 = puVar18 + 1;
  }
  puVar16 = auStack_110;
  CFastVB__DispatchIndirect_00656f3c();
  puVar14 = auStack_dc;
  puVar6 = auStack_5c;
  puVar29 = auStack_15c;
  CFastVB__DispatchIndirect_00656f3c();
  cVar3 = cStack_20;
  fStack_214 = (float)DAT_0089ce14 / (float)(iStack_1a8 / 2);
  puStack_288 = (undefined1 *)(iStack_1a4 / 2);
  _DAT_00888fb4 = 0;
  fStack_210 = (float)DAT_0089ce14 / (float)(int)puStack_288;
  DAT_00855178 = DAT_00855170;
  if (DAT_00855170 == (undefined4 *)0x0) {
    piVar8 = (int *)0x0;
  }
  else {
    piVar8 = (int *)*DAT_00855170;
  }
  while (piVar8 != (int *)0x0) {
    piVar10 = piVar8 + 2;
    puVar27 = &stack0xfffffd88;
    (**(code **)piVar8[2])(puVar27,puVar29,puVar6,puVar14,puVar7,puVar4,puVar16);
    pvVar5 = (void *)(**(code **)(*piVar10 + 0x54))();
    if (pvVar5 != (void *)0x0) {
      this = piVar8 + 0xf;
      if ((piVar8[0xd] & 0x80000000U) == 0) {
        this = &DAT_0083d9c0;
      }
      CSquadNormal__Helper_0040d2c0(this,auStack_1ac,pvVar5,puVar27);
      unaff_ESI = unaff_ESI + *extraout_EAX;
      unaff_EBP = unaff_EBP + extraout_EAX[1];
      unaff_EBX = unaff_EBX + extraout_EAX[2];
    }
    Vec3__SetXYZ();
    CUnitAI__Helper_00477ba0();
    fVar20 = (float10)(**(code **)(*piVar8 + 0x34))();
    fVar31 = (float)(fVar20 / ((float10)(float)extraout_ST0 + (float10)_DAT_005d8580));
    if ((cVar3 != '\0') &&
       ((((uVar1 = piVar8[0xd], (uVar1 & 0x10) != 0 || ((uVar1 & 0x100) != 0)) && ((uVar1 & 8) == 0)
         ) && (iVar11 = (**(code **)(*piVar8 + 0x28))(), iVar11 == 0)))) {
      CVBufTexture__Helper_00477b70
                (&DAT_009c7550,piVar8,(void *)(_DAT_005d8568 / fVar31),(float)puVar27);
    }
    puVar28 = auStack_16c;
    puVar27 = &stack0xfffffd84;
    puVar25 = auStack_26c;
    CVBufTexture__Helper_0057600b();
    puVar23 = auStack_178;
    fVar20 = (float10)(**(code **)(*piVar10 + 0x20))(puVar23,puVar25,puVar27,puVar28);
    Vec3__ScaleToOut(&fStack_1e8,auStack_188,(void *)(float)fVar20,(float)puVar23);
    Vec3__Add(&puStack_288,auStack_1c8,extraout_EAX_00,puVar23);
    pfVar12 = &fStack_248;
    uVar21 = extraout_EAX_01;
    CVBufTexture__Helper_0057600b();
    pfStack_284 = (float *)((float)pfStack_284 / unaff_EBP + _DAT_005d8568);
    fStack_254 = fStack_254 / fStack_248 + _DAT_005d8568;
    fStack_250 = fStack_250 / fStack_248 + _DAT_005d8568;
    fVar20 = (float10)(**(code **)(*piVar10 + 0x20))(pfVar12,uVar21);
    fVar31 = -(float)auStack_18c;
    if ((((fVar31 < fStack_268) && (fStack_268 < (float)auStack_18c + fStack_214)) &&
        ((fVar31 < fStack_264 && (fStack_264 < (float)auStack_18c + fStack_210)))) ||
       (((float10)unaff_ESI < fVar20 * fVar20 || ((piVar8[0xd] & 0x10000U) != 0)))) {
      if (((cStack_1c != '\0') &&
          (((uVar1 = piVar8[0xd], (uVar1 & 0x30) != 0 || ((uVar1 & 0x100) != 0)) &&
           ((uVar1 & 8) == 0)))) && (iVar11 = (**(code **)(*piVar8 + 0x28))(), iVar11 == 0)) {
        CDXEngine__BuildProjectedSprites(&DAT_009c7550,piVar8);
      }
      if (cStack_24 != '\0') {
        (**(code **)(*piVar8 + 0x94))();
      }
      (**(code **)(*piVar8 + 0x90))(0);
    }
    DAT_00855178 = (undefined4 *)DAT_00855178[1];
    if (DAT_00855178 == (undefined4 *)0x0) {
      piVar8 = (int *)0x0;
    }
    else {
      piVar8 = (int *)*DAT_00855178;
    }
  }
  fVar31 = 2.24208e-44;
  fStack_290 = 0.0;
  do {
    iVar11 = 1 << (SUB41(fStack_290,0) & 0x1f);
    puVar6 = (undefined1 *)(*(int *)((int)fStack_254 + 8) / iVar11);
    iStack_21c = *(int *)((int)fStack_254 + 0x18) / iVar11 + -1;
    puVar14 = (undefined1 *)(*(int *)((int)fStack_254 + 0x20) / iVar11 + 2);
    iStack_23c = *(int *)((int)fStack_254 + 0x1c) / iVar11 + -1;
    puVar7 = (undefined1 *)(*(int *)((int)fStack_254 + 0x24) / iVar11 + 2);
    if (iStack_21c < 0) {
      iStack_21c = 0;
    }
    if ((int)puVar6 < (int)puVar14) {
      puVar14 = puVar6;
    }
    if (iStack_23c < 0) {
      iStack_23c = 0;
    }
    if ((int)puVar6 < (int)puVar7) {
      puVar7 = puVar6;
    }
    fVar13 = (float)(iVar11 * 8);
    fStack_1f0 = (float)((int)fVar13 * (int)fVar13 * 2) * _DAT_005d85ec;
    if (iStack_23c < (int)puVar7) {
      fStack_1ec = (float)(0x40 >> (SUB41(fStack_290,0) & 0x1f));
      iStack_228 = (int)fVar13 * iStack_23c;
      fStack_250 = (float)((iStack_23c + 2) * iVar11);
      fStack_220 = (float)((iStack_23c + -1) * iVar11);
      iVar9 = iStack_21c;
      puStack_288 = puVar14;
      fStack_244 = fVar13;
      iStack_1f8 = iVar11;
      do {
        pvStack_24c = (void *)(*(int *)((int)fVar31 + DAT_00704290) +
                              ((int)(short)iStack_23c * (int)fStack_1ec + (int)(short)iVar9) * 8);
        if (iVar9 < (int)puVar14) {
          fStack_248 = (float)((int)fVar13 * iVar9);
          fStack_218 = (float)(int)fStack_244 * _DAT_005d85ec;
          fStack_224 = (float)((iVar9 + 2) * iVar11);
          afStack_174[0] = (float)iStack_228 + fStack_218;
          fStack_240 = (float)((iVar9 + -1) * iVar11);
          iStack_258 = (int)puVar14 - iVar9;
          do {
            bVar2 = false;
            fVar30 = 0.0;
            fVar13 = fStack_20c - ((float)(int)fStack_248 + fStack_218);
            fStack_1fc = (fVar13 * fVar13 +
                         (fStack_208 - afStack_174[0]) * (fStack_208 - afStack_174[0])) - fStack_1f0
            ;
            if (*(int *)((int)pvStack_24c + 4) != 0) {
              fVar13 = *(float *)((int)fStack_254 + 0x18);
              pfStack_284 = (float *)fStack_240;
              if ((int)fStack_240 < (int)fVar13) {
                pfStack_284 = (float *)fVar13;
              }
              fVar19 = fStack_224;
              if ((int)fStack_224 < (int)fVar13) {
                fVar19 = fVar13;
              }
              fVar13 = *(float *)((int)fStack_254 + 0x20);
              if ((int)fVar13 < (int)pfStack_284) {
                pfStack_284 = (float *)fVar13;
              }
              if ((int)fVar13 < (int)fVar19) {
                fVar19 = fVar13;
              }
              fVar13 = *(float *)((int)fStack_254 + 0x1c);
              fVar17 = fStack_220;
              if ((int)fStack_220 < (int)fVar13) {
                fVar17 = fVar13;
              }
              fVar15 = fStack_250;
              if ((int)fStack_250 < (int)fVar13) {
                fVar15 = fVar13;
              }
              fVar13 = *(float *)((int)fStack_254 + 0x24);
              if ((int)fVar13 < (int)fVar17) {
                fVar17 = fVar13;
              }
              if ((int)fVar13 < (int)fVar15) {
                fVar15 = fVar13;
              }
              if ((int)fVar17 < (int)fVar15) {
                do {
                  if ((int)pfStack_284 < (int)fVar19) {
                    pfVar12 = pfStack_284;
                    do {
                      iVar11 = *(int *)((int)fStack_254 + 8) * (int)fVar17 + (int)pfVar12;
                      if (*(char *)(*(int *)((int)fStack_254 + 0xc) + iVar11 * 2) <
                          *(char *)(*(int *)((int)fStack_254 + 0xc) + iVar11 * 2 + 1)) {
                        fVar30 = 1.4013e-45;
                      }
                      else {
                        bVar2 = true;
                        if (fVar30 != 0.0) {
                          pfVar12 = (float *)fVar19;
                          fVar17 = fVar15;
                        }
                      }
                      pfVar12 = (float *)((int)pfVar12 + 1);
                      iVar11 = iStack_1f8;
                    } while ((int)pfVar12 < (int)fVar19);
                  }
                  fVar17 = (float)((int)fVar17 + 1);
                } while ((int)fVar17 < (int)fVar15);
                if (bVar2) {
                  CCollisionSeekingRound__Helper_00491d80(&DAT_00704200,pvStack_24c,(int)puVar29);
                  iVar9 = extraout_EAX_02;
                  fVar13 = fVar30;
                  while (iVar9 != 0) {
                    piVar8 = (int *)CMapWhoEntry__GetOwner();
                    if ((piVar8[0xd] & 0x800000U) != 0) {
                      if ((piVar8[0xd] & 0x2000000U) != 0) {
                        if (fStack_1fc <
                            (g_MeshQualityDistance + _DAT_005d85cc) *
                            (g_MeshQualityDistance + _DAT_005d85cc)) {
                          while (iVar9 != 0) {
                            iVar9 = CCollisionSeekingRound__Helper_00491d90(&DAT_00704200);
                            piVar10 = piVar8;
                            if (iVar9 != 0) {
                              piVar10 = (int *)CMapWhoEntry__GetOwner();
                            }
                            (**(code **)(*piVar8 + 0x90))(0);
                            piVar8 = piVar10;
                          }
                        }
                        break;
                      }
                      piVar10 = piVar8 + 2;
                      (**(code **)piVar8[2])(&stack0xfffffd88);
                      iVar9 = (**(code **)(*piVar10 + 0x54))();
                      if (iVar9 != 0) {
                        Vec3__SetXYZ();
                        puVar7 = (undefined1 *)(fStack_1bc + (float)puVar7);
                        unaff_EBX = unaff_EBX + fStack_1b4;
                      }
                      Vec3__SetXYZ();
                      fStack_290 = fStack_1ec * fStack_1ec +
                                   fStack_1e8 * fStack_1e8 + local_1e4[0] * local_1e4[0];
                      fVar20 = (float10)(**(code **)(*piVar8 + 0x34))();
                      fStack_1f4 = (float)(fVar20 / ((float10)fVar15 + (float10)_DAT_005d8580));
                      if (fVar30 != 0.0) {
                        puVar6 = auStack_168;
                        puVar14 = &stack0xfffffd88;
                        pfVar12 = &fStack_268;
                        CVBufTexture__Helper_0057600b();
                        (**(code **)(*piVar10 + 0x20))(pfVar12,puVar14,puVar6);
                        Vec3__SetXYZ();
                        Vec3__SetXYZ();
                        pfVar26 = afStack_174;
                        pfVar24 = &fStack_1b4;
                        pfVar22 = &fStack_244;
                        CVBufTexture__Helper_0057600b();
                        fVar31 = fVar31 / unaff_EBX + _DAT_005d8568;
                        puVar7 = (undefined1 *)((float)puVar7 / unaff_EBX + _DAT_005d8568);
                        fStack_250 = fStack_250 / fStack_244 + _DAT_005d8568;
                        pvStack_24c = (void *)((float)pvStack_24c / fStack_244 + _DAT_005d8568);
                        fVar20 = (float10)(**(code **)(*piVar10 + 0x20))
                                                    (pfVar22,pfVar24,pfVar26,pfVar12,puVar14,
                                                     fStack_250 - fVar31);
                        pfStack_284 = (float *)-fVar13;
                        if ((((fStack_268 <= (float)pfStack_284) ||
                             (fVar13 + fStack_214 <= fStack_268)) ||
                            ((fStack_264 <= (float)pfStack_284 ||
                             (fVar13 + fStack_210 <= fStack_264)))) &&
                           ((fVar20 * fVar20 <= (float10)fVar15 && ((piVar8[0xd] & 0x10000U) == 0)))
                           ) goto LAB_00477a47;
                      }
                      if ((cStack_1c != '\0') &&
                         ((((uVar1 = piVar8[0xd], (uVar1 & 0x30) != 0 || ((uVar1 & 0x100) != 0)) &&
                           ((uVar1 & 8) == 0)) &&
                          (iVar9 = (**(code **)(*piVar8 + 0x28))(), iVar9 == 0)))) {
                        CDXEngine__BuildProjectedSprites(&DAT_009c7550,piVar8);
                      }
                      if (cStack_24 != '\0') {
                        (**(code **)(*piVar8 + 0x94))();
                      }
                      if (((cStack_20 != '\0') &&
                          ((uVar1 = piVar8[0xd], (uVar1 & 0x10) != 0 || ((uVar1 & 0x100) != 0)))) &&
                         (((uVar1 & 0x80000) == 0 &&
                          ((((uVar1 & 8) == 0 &&
                            (iVar9 = (**(code **)(*piVar8 + 0x28))(), iVar9 == 0)) &&
                           ((fVar13 = _DAT_005d8568 / fStack_1f4, DAT_0089d680 == '\0' &&
                            (fVar13 < (float)(&g_MeshQualityLodTable)[DAT_009c7b0c * 2])))))))) {
                        CRenderQueue__InsertSortedByDepth(&DAT_009c7550,piVar8,fVar13);
                      }
                      (**(code **)(*piVar8 + 0x90))(0);
                    }
LAB_00477a47:
                    iVar9 = CCollisionSeekingRound__Helper_00491d90(&DAT_00704200);
                  }
                }
              }
            }
            fStack_248 = (float)((int)fStack_248 + (int)fStack_244);
            fStack_240 = (float)((int)fStack_240 + iVar11);
            fStack_224 = (float)((int)fStack_224 + iVar11);
            pvStack_24c = (void *)((int)pvStack_24c + 8);
            iStack_258 = iStack_258 + -1;
            fVar13 = fStack_244;
            puVar14 = puStack_288;
            iVar9 = iStack_21c;
          } while (iStack_258 != 0);
        }
        iStack_228 = iStack_228 + (int)fVar13;
        fStack_220 = (float)((int)fStack_220 + iVar11);
        iStack_23c = iStack_23c + 1;
        fStack_250 = (float)((int)fStack_250 + iVar11);
      } while (iStack_23c < (int)puVar7);
    }
    fStack_290 = (float)((int)fStack_290 + 1);
    fVar31 = (float)((int)fVar31 + -4);
    if (1 < (int)fStack_290) {
      return;
    }
  } while( true );
}
