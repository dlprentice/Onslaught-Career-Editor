/* address: 0x004ec2f0 */
/* name: CStaticShadows__BuildShadowMaps */
/* signature: undefined CStaticShadows__BuildShadowMaps(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CStaticShadows__BuildShadowMaps(int *param_1)

{
  bool bVar1;
  void *pvVar2;
  char cVar3;
  int *array;
  int iVar4;
  undefined4 extraout_EAX;
  undefined4 uVar5;
  void *pvVar6;
  void *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  uint uVar7;
  int iVar8;
  float fVar9;
  float *pfVar10;
  int iVar11;
  void *unaff_EDI;
  double dVar12;
  float fStack_6d8;
  float fStack_6d4;
  float fStack_6d0;
  undefined4 uStack_6cc;
  float fStack_6c8;
  float fStack_6c4;
  float fStack_6c0;
  float fStack_6bc;
  float fStack_6b8;
  float fStack_6b4;
  float fStack_6b0;
  float fStack_6ac;
  float fStack_6a8;
  float fStack_6a4;
  int iStack_6a0;
  float fStack_69c;
  int iStack_698;
  float fStack_694;
  float fStack_690;
  longlong lStack_68c;
  float fStack_684;
  float fStack_680;
  float fStack_67c;
  int iStack_678;
  float fStack_674;
  float fStack_670;
  float fStack_66c;
  float fStack_664;
  float fStack_660;
  float fStack_65c;
  float fStack_654;
  float fStack_650;
  float fStack_64c;
  int iStack_644;
  int iStack_640;
  int iStack_63c;
  float fStack_638;
  float fStack_634;
  int local_630;
  float fStack_62c;
  float fStack_628;
  float fStack_624;
  undefined4 uStack_620;
  int *piStack_61c;
  void *pvStack_618;
  int iStack_614;
  undefined4 uStack_610;
  undefined4 uStack_60c;
  undefined4 uStack_608;
  undefined4 uStack_604;
  float fStack_600;
  float fStack_5fc;
  float fStack_5f8;
  float fStack_5f0;
  float fStack_5ec;
  float fStack_5e8;
  undefined4 uStack_5e4;
  float fStack_5e0;
  float fStack_5dc;
  float fStack_5d8;
  undefined4 uStack_5d4;
  float fStack_5d0;
  float fStack_5cc;
  float fStack_5c8;
  undefined4 uStack_5c4;
  undefined1 auStack_5c0 [48];
  float fStack_590;
  float fStack_58c;
  float fStack_588;
  undefined4 uStack_584;
  float fStack_580;
  float fStack_57c;
  float fStack_578;
  undefined4 uStack_574;
  float fStack_570;
  float fStack_56c;
  float fStack_568;
  undefined4 uStack_564;
  float fStack_560;
  float fStack_55c;
  float fStack_558;
  undefined4 uStack_554;
  float fStack_550;
  float fStack_54c;
  float fStack_548;
  undefined4 uStack_544;
  float fStack_540;
  float fStack_53c;
  float fStack_538;
  undefined4 uStack_534;
  float fStack_530;
  float fStack_52c;
  float fStack_528;
  undefined4 uStack_524;
  float fStack_520;
  float fStack_51c;
  float fStack_518;
  undefined4 uStack_514;
  float fStack_510;
  float fStack_50c;
  float fStack_508;
  undefined4 uStack_504;
  float fStack_500;
  float fStack_4fc;
  float fStack_4f8;
  undefined4 uStack_4f4;
  float fStack_4f0;
  undefined4 uStack_4ec;
  float fStack_4e8;
  undefined4 uStack_4e4;
  float fStack_4e0;
  float fStack_4dc;
  float fStack_4d8;
  undefined4 uStack_4d4;
  float fStack_4d0;
  undefined4 uStack_4cc;
  float fStack_4c8;
  undefined4 uStack_4c4;
  float fStack_4c0;
  float fStack_4bc;
  float fStack_4b8;
  undefined4 uStack_4b4;
  float fStack_4b0;
  float fStack_4ac;
  float fStack_4a8;
  undefined4 uStack_4a4;
  float fStack_4a0;
  float fStack_49c;
  float fStack_498;
  undefined4 uStack_494;
  short *psStack_490;
  short *psStack_48c;
  float afStack_484 [5];
  float fStack_470;
  float fStack_46c;
  undefined4 uStack_468;
  float fStack_464;
  float fStack_460;
  float fStack_45c;
  undefined4 uStack_458;
  float fStack_454;
  float fStack_450;
  float fStack_44c;
  undefined4 uStack_448;
  float fStack_444;
  float fStack_440;
  float fStack_43c;
  undefined4 uStack_438;
  float fStack_434;
  float fStack_430;
  float fStack_42c;
  undefined4 uStack_428;
  float fStack_424;
  undefined4 uStack_420;
  float fStack_41c;
  undefined4 uStack_418;
  float fStack_414;
  undefined4 uStack_410;
  float fStack_40c;
  undefined4 uStack_408;
  undefined1 auStack_404 [16];
  float fStack_3f4;
  float fStack_3f0;
  float fStack_3ec;
  undefined4 uStack_3e8;
  undefined4 uStack_3e4;
  undefined4 uStack_3e0;
  undefined4 uStack_3dc;
  undefined4 uStack_3d8;
  float fStack_3d4;
  undefined4 uStack_3d0;
  float fStack_3cc;
  undefined4 uStack_3c8;
  float fStack_3c4;
  undefined4 uStack_3c0;
  float fStack_3bc;
  undefined4 uStack_3b8;
  undefined4 uStack_3b4;
  undefined4 uStack_3b0;
  undefined4 uStack_3ac;
  undefined4 uStack_3a8;
  float fStack_3a4;
  float fStack_3a0;
  float fStack_39c;
  float fStack_364;
  float fStack_360;
  float fStack_35c;
  float fStack_344;
  float fStack_340;
  float fStack_33c;
  undefined **appuStack_324 [5];
  float fStack_310;
  float fStack_30c;
  float fStack_308;
  undefined4 uStack_304;
  float fStack_300;
  float fStack_2fc;
  float fStack_2f8;
  undefined4 uStack_2f4;
  undefined **appuStack_2f0 [5];
  float fStack_2dc;
  float fStack_2d8;
  float fStack_2d4;
  undefined4 uStack_2d0;
  float fStack_2cc;
  float fStack_2c8;
  float fStack_2c4;
  undefined4 uStack_2c0;
  undefined **appuStack_2bc [5];
  float fStack_2a8;
  float fStack_2a4;
  float fStack_2a0;
  undefined4 uStack_29c;
  float fStack_298;
  float fStack_294;
  float fStack_290;
  undefined4 uStack_28c;
  undefined **appuStack_288 [5];
  float fStack_274;
  float fStack_270;
  float fStack_26c;
  undefined4 uStack_268;
  float fStack_264;
  float fStack_260;
  float fStack_25c;
  undefined4 uStack_258;
  undefined **appuStack_254 [5];
  float fStack_240;
  float fStack_23c;
  float fStack_238;
  undefined4 uStack_234;
  float fStack_230;
  float fStack_22c;
  float fStack_228;
  undefined4 uStack_224;
  undefined **appuStack_220 [5];
  float fStack_20c;
  float fStack_208;
  float fStack_204;
  undefined4 uStack_200;
  float fStack_1fc;
  float fStack_1f8;
  float fStack_1f4;
  undefined4 uStack_1f0;
  undefined **appuStack_1ec [5];
  float fStack_1d8;
  undefined4 uStack_1d4;
  float fStack_1d0;
  undefined4 uStack_1cc;
  undefined4 uStack_1c8;
  undefined4 uStack_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined **appuStack_1b8 [5];
  float fStack_1a4;
  undefined4 uStack_1a0;
  float fStack_19c;
  undefined4 uStack_198;
  undefined4 uStack_194;
  undefined4 uStack_190;
  undefined4 uStack_18c;
  undefined4 uStack_188;
  undefined1 auStack_184 [16];
  undefined1 auStack_174 [16];
  undefined1 auStack_164 [48];
  undefined1 auStack_134 [16];
  undefined1 auStack_124 [16];
  char acStack_114 [256];
  void *pvStack_14;
  undefined1 *puStack_10;
  undefined4 uStack_c;

  uStack_c = 0xffffffff;
  puStack_10 = &LAB_005d4f80;
  pvStack_14 = ExceptionList;
  if (*(int **)(*param_1 + 0x30) == (int *)0x0) {
    local_630 = 0;
    ExceptionList = &pvStack_14;
  }
  else {
    ExceptionList = &pvStack_14;
    local_630 = (**(code **)(**(int **)(*param_1 + 0x30) + 0x24))();
  }
  iVar8 = *(int *)(local_630 + 0x15c);
  param_1[3] = iVar8;
  piStack_61c = (int *)OID__AllocObject(iVar8 * 0x1c + 4,0x70,
                                        s_C__dev_ONSLAUGHT2_StaticShadows__006329f8,0x18a);
  uStack_c = 0;
  if (piStack_61c == (int *)0x0) {
    array = (int *)0x0;
  }
  else {
    array = piStack_61c + 1;
    *piStack_61c = iVar8;
    eh_vector_constructor_iterator(array,0x1c,iVar8,&LAB_004ee0c0,CStaticShadows__Destructor);
  }
  param_1[2] = (int)array;
  fStack_624 = DAT_009c8020;
  iStack_640 = 0x200;
  fStack_634 = 7.17465e-43;
  fStack_62c = DAT_009c8018;
  uStack_c = 0xffffffff;
  fStack_628 = DAT_009c801c;
  uStack_620 = DAT_009c8024;
  iStack_63c = 0;
  fStack_638 = 0.0;
  iStack_644 = 0;
  if (0 < param_1[3]) {
    do {
      iVar4 = iStack_644;
      iVar8 = *(int *)(*(int *)(local_630 + 0x160) + iStack_644 * 4);
      iStack_614 = iVar8;
      pvStack_618 = (void *)CMesh__Helper_004b0cd0(iVar8);
      if ((pvStack_618 == (void *)0x0) ||
         ((*(int *)(iVar8 + 0x8c) != 1 && (*(int *)(iVar8 + 0x8c) != 6)))) {
        *(undefined4 *)(param_1[2] + 0x14 + iVar4 * 0x1c) = 0;
      }
      else {
        iStack_678 = iVar4 * 0x1c;
        *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 1;
        piStack_61c = *(int **)(iVar8 + 0x100);
        iVar4 = OID__AllocObject(0xb8,0x61,s_C__dev_ONSLAUGHT2_StaticShadows__006329f8,0x1a7);
        lStack_68c = CONCAT44(lStack_68c._4_4_,iVar4);
        uStack_c = 1;
        if (iVar4 == 0) {
          uVar5 = 0;
        }
        else {
          CInfluenceMap__ResetRuntimeState(iVar4);
          uVar5 = extraout_EAX;
        }
        uStack_c = 0xffffffff;
        *(undefined4 *)(iVar8 + 0x100) = uVar5;
        cVar3 = CPolyBucket__Build();
        if ((cVar3 == '\0') && (pvVar6 = *(void **)(iVar8 + 0x100), pvVar6 != (void *)0x0)) {
          CInfluenceMap__FreeRuntimeBuffers((int)pvVar6);
          OID__FreeObject(pvVar6);
          *(undefined4 *)(iVar8 + 0x100) = 0;
        }
        fStack_6bc = fStack_624 * _DAT_005df3f4;
        pfVar10 = *(float **)(iVar8 + 0xfc);
        iStack_6a0 = 0x200;
        fStack_684 = 7.17465e-43;
        fStack_6c4 = fStack_628 * _DAT_005df3f4;
        iStack_698 = 0;
        fStack_680 = 0.0;
        fStack_6c0 = fStack_62c * _DAT_005df3f4;
        CMCMech__Helper_004b0fb0();
        fStack_6b0 = pfVar10[4];
        fStack_6b4 = pfVar10[5];
        fStack_6ac = pfVar10[6];
        fStack_69c = fStack_39c +
                     fStack_654 * *pfVar10 + fStack_64c * pfVar10[2] + fStack_650 * pfVar10[1];
        fStack_6c8 = fStack_3a0 +
                     fStack_664 * *pfVar10 + fStack_65c * pfVar10[2] + fStack_660 * pfVar10[1];
        fStack_6b8 = fStack_66c * pfVar10[2] + fStack_670 * pfVar10[1] + fStack_674 * *pfVar10 +
                     fStack_3a4;
        fStack_690 = -fStack_6b0;
        fStack_694 = -fStack_6b4;
        fStack_67c = -fStack_6ac;
        fStack_6a4 = fStack_694 * fStack_650 + fStack_67c * fStack_64c + fStack_690 * fStack_654;
        fStack_6a8 = fStack_694 * fStack_660 + fStack_67c * fStack_65c + fStack_690 * fStack_664;
        fStack_6d8 = fStack_694 * fStack_670 + fStack_67c * fStack_66c + fStack_690 * fStack_674;
        lStack_68c = CONCAT44(lStack_68c._4_4_,fStack_6d8);
        fStack_6d0 = fStack_6a4 + fStack_69c;
        fStack_6d4 = fStack_6a8 + fStack_6c8;
        fStack_6d8 = fStack_6d8 + fStack_6b8;
        uStack_6cc = uStack_4a4;
        fStack_4b0 = fStack_6d8;
        fStack_4ac = fStack_6d4;
        fStack_4a8 = fStack_6d0;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_548 = fStack_6bc + fStack_6d0;
          fStack_54c = fStack_6c4 + fStack_6d4;
          fStack_550 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_310 = fStack_6d8;
          fStack_30c = fStack_6d4;
          fStack_308 = fStack_6d0;
          uStack_304 = uStack_6cc;
          fStack_300 = fStack_550;
          fStack_2fc = fStack_54c;
          fStack_2f8 = fStack_548;
          uStack_2f4 = uStack_544;
          appuStack_324[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 2;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_324,(int)afStack_484,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_324[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_498 = (float)dVar12;
          fStack_4a0 = fStack_6d8;
          fStack_49c = fStack_6d4;
          afStack_484[0] = fStack_6d8;
          afStack_484[1] = fStack_6d4;
          afStack_484[3] = (float)uStack_494;
          afStack_484[2] = fStack_498;
        }
        fStack_6d0 = fStack_694 * fStack_650 + fStack_67c * fStack_64c + fStack_6b0 * fStack_654;
        lStack_68c = CONCAT44(lStack_68c._4_4_,fStack_6d0);
        fStack_6a8 = fStack_694 * fStack_660 + fStack_67c * fStack_65c + fStack_6b0 * fStack_664;
        fStack_6a4 = fStack_694 * fStack_670 + fStack_67c * fStack_66c + fStack_674 * fStack_6b0;
        fStack_6d0 = fStack_6d0 + fStack_69c;
        fStack_6d4 = fStack_6a8 + fStack_6c8;
        fStack_6d8 = fStack_6a4 + fStack_6b8;
        uStack_6cc = uStack_4b4;
        fStack_4c0 = fStack_6d8;
        fStack_4bc = fStack_6d4;
        fStack_4b8 = fStack_6d0;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_4f8 = fStack_6bc + fStack_6d0;
          fStack_4fc = fStack_6c4 + fStack_6d4;
          fStack_500 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_240 = fStack_6d8;
          fStack_23c = fStack_6d4;
          fStack_238 = fStack_6d0;
          uStack_234 = uStack_6cc;
          fStack_230 = fStack_500;
          fStack_22c = fStack_4fc;
          fStack_228 = fStack_4f8;
          uStack_224 = uStack_4f4;
          appuStack_254[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 3;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_254,(int)(afStack_484 + 4),(void *)0x0,
                     (int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_254[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_578 = (float)dVar12;
          fStack_580 = fStack_6d8;
          fStack_57c = fStack_6d4;
          afStack_484[4] = fStack_6d8;
          fStack_470 = fStack_6d4;
          uStack_468 = uStack_574;
          fStack_46c = fStack_578;
        }
        fStack_6d0 = fStack_67c * fStack_64c + fStack_6b4 * fStack_650 + fStack_690 * fStack_654;
        lStack_68c = CONCAT44(lStack_68c._4_4_,fStack_6d0);
        fStack_6a8 = fStack_67c * fStack_65c + fStack_6b4 * fStack_660 + fStack_690 * fStack_664;
        fStack_6a4 = fStack_67c * fStack_66c + fStack_690 * fStack_674 + fStack_670 * fStack_6b4;
        fStack_6d0 = fStack_6d0 + fStack_69c;
        fStack_6d4 = fStack_6a8 + fStack_6c8;
        fStack_6d8 = fStack_6a4 + fStack_6b8;
        uStack_6cc = uStack_554;
        fStack_560 = fStack_6d8;
        fStack_55c = fStack_6d4;
        fStack_558 = fStack_6d0;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_538 = fStack_6bc + fStack_6d0;
          fStack_53c = fStack_6c4 + fStack_6d4;
          fStack_540 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_2a8 = fStack_6d8;
          fStack_2a4 = fStack_6d4;
          fStack_2a0 = fStack_6d0;
          uStack_29c = uStack_6cc;
          fStack_298 = fStack_540;
          fStack_294 = fStack_53c;
          fStack_290 = fStack_538;
          uStack_28c = uStack_534;
          appuStack_2bc[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 4;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_2bc,(int)&fStack_464,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_2bc[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_5e8 = (float)dVar12;
          fStack_5f0 = fStack_6d8;
          fStack_5ec = fStack_6d4;
          fStack_464 = fStack_6d8;
          fStack_460 = fStack_6d4;
          uStack_458 = uStack_5e4;
          fStack_45c = fStack_5e8;
        }
        fStack_6d0 = fStack_67c * fStack_64c + fStack_6b4 * fStack_650 + fStack_6b0 * fStack_654;
        lStack_68c = CONCAT44(lStack_68c._4_4_,fStack_6d0);
        fStack_6a8 = fStack_67c * fStack_65c + fStack_6b4 * fStack_660 + fStack_6b0 * fStack_664;
        fStack_6a4 = fStack_67c * fStack_66c + fStack_674 * fStack_6b0 + fStack_670 * fStack_6b4;
        fStack_6d0 = fStack_6d0 + fStack_69c;
        fStack_6d4 = fStack_6a8 + fStack_6c8;
        fStack_6d8 = fStack_6a4 + fStack_6b8;
        uStack_6cc = uStack_4d4;
        fStack_4e0 = fStack_6d8;
        fStack_4dc = fStack_6d4;
        fStack_4d8 = fStack_6d0;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_5c8 = fStack_6bc + fStack_6d0;
          fStack_5cc = fStack_6c4 + fStack_6d4;
          fStack_5d0 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_2dc = fStack_6d8;
          fStack_2d8 = fStack_6d4;
          fStack_2d4 = fStack_6d0;
          uStack_2d0 = uStack_6cc;
          fStack_2cc = fStack_5d0;
          fStack_2c8 = fStack_5cc;
          fStack_2c4 = fStack_5c8;
          uStack_2c0 = uStack_5c4;
          appuStack_2f0[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 5;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_2f0,(int)&fStack_454,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_2f0[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_518 = (float)dVar12;
          fStack_520 = fStack_6d8;
          fStack_51c = fStack_6d4;
          fStack_454 = fStack_6d8;
          fStack_450 = fStack_6d4;
          uStack_448 = uStack_514;
          fStack_44c = fStack_518;
        }
        fStack_6d0 = fStack_694 * fStack_650 + fStack_6ac * fStack_64c + fStack_690 * fStack_654;
        lStack_68c = CONCAT44(lStack_68c._4_4_,fStack_6d0);
        fStack_6a8 = fStack_694 * fStack_660 + fStack_6ac * fStack_65c + fStack_690 * fStack_664;
        fStack_6a4 = fStack_694 * fStack_670 + fStack_690 * fStack_674 + fStack_66c * fStack_6ac;
        fStack_6d0 = fStack_6d0 + fStack_69c;
        fStack_6d4 = fStack_6a8 + fStack_6c8;
        fStack_6d8 = fStack_6a4 + fStack_6b8;
        uStack_6cc = uStack_584;
        fStack_590 = fStack_6d8;
        fStack_58c = fStack_6d4;
        fStack_588 = fStack_6d0;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_5d8 = fStack_6bc + fStack_6d0;
          fStack_5dc = fStack_6c4 + fStack_6d4;
          fStack_5e0 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_274 = fStack_6d8;
          fStack_270 = fStack_6d4;
          fStack_26c = fStack_6d0;
          uStack_268 = uStack_6cc;
          fStack_264 = fStack_5e0;
          fStack_260 = fStack_5dc;
          fStack_25c = fStack_5d8;
          uStack_258 = uStack_5d4;
          appuStack_288[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 6;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_288,(int)&fStack_444,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_288[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_568 = (float)dVar12;
          fStack_570 = fStack_6d8;
          fStack_56c = fStack_6d4;
          fStack_444 = fStack_6d8;
          fStack_440 = fStack_6d4;
          uStack_438 = uStack_564;
          fStack_43c = fStack_568;
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        fStack_6d8 = fStack_3f4;
        fStack_6d4 = fStack_3f0;
        fStack_6d0 = fStack_3ec;
        uStack_6cc = uStack_3e8;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          fStack_508 = fStack_6bc + fStack_6d0;
          fStack_50c = fStack_6c4 + fStack_6d4;
          fStack_510 = fStack_6c0 + fStack_6d8;
          Vec3__SetXYZ();
          fStack_20c = fStack_6d8;
          fStack_208 = fStack_6d4;
          fStack_204 = fStack_6d0;
          uStack_200 = uStack_6cc;
          fStack_1fc = fStack_510;
          fStack_1f8 = fStack_50c;
          fStack_1f4 = fStack_508;
          uStack_1f0 = uStack_504;
          appuStack_220[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 7;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_220,(int)&fStack_434,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_220[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_528 = (float)dVar12;
          fStack_530 = fStack_6d8;
          fStack_52c = fStack_6d4;
          fStack_434 = fStack_6d8;
          fStack_430 = fStack_6d4;
          uStack_428 = uStack_524;
          fStack_42c = fStack_528;
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        fStack_6d8 = fStack_3d4;
        fStack_6d4 = (float)uStack_3d0;
        fStack_6d0 = fStack_3cc;
        uStack_6cc = uStack_3c8;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          Vec3__SetXYZ();
          CGeneralVolume__ctor_like_0040b100(appuStack_1b8);
          fStack_1a4 = fStack_6d8;
          uStack_1a0 = fStack_6d4;
          fStack_19c = fStack_6d0;
          uStack_198 = uStack_6cc;
          uStack_194 = uStack_3b4;
          uStack_190 = uStack_3b0;
          uStack_18c = uStack_3ac;
          uStack_188 = uStack_3a8;
          appuStack_1b8[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 8;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_1b8,(int)&fStack_424,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_1b8[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_4e8 = (float)dVar12;
          fStack_4f0 = fStack_6d8;
          uStack_4ec = fStack_6d4;
          fStack_424 = fStack_6d8;
          uStack_420 = fStack_6d4;
          uStack_418 = uStack_4e4;
          fStack_41c = fStack_4e8;
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        fStack_6d8 = fStack_3c4;
        fStack_6d4 = (float)uStack_3c0;
        fStack_6d0 = fStack_3bc;
        uStack_6cc = uStack_3b8;
        dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
        if ((double)fStack_6d0 <= dVar12) {
          Vec3__SetXYZ();
          CGeneralVolume__ctor_like_0040b100(appuStack_1ec);
          fStack_1d8 = fStack_6d8;
          uStack_1d4 = fStack_6d4;
          fStack_1d0 = fStack_6d0;
          uStack_1cc = uStack_6cc;
          uStack_1c8 = uStack_3e4;
          uStack_1c4 = uStack_3e0;
          uStack_1c0 = uStack_3dc;
          uStack_1bc = uStack_3d8;
          appuStack_1ec[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          uStack_c = 9;
          CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)appuStack_1ec,(int)&fStack_414,(void *)0x0,(int)unaff_EDI);
          uStack_c = 0xffffffff;
          appuStack_1ec[0] = &PTR_LAB_005d892c;
        }
        else {
          dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_6d8);
          fStack_4c8 = (float)dVar12;
          fStack_4d0 = fStack_6d8;
          uStack_4cc = fStack_6d4;
          fStack_414 = fStack_6d8;
          uStack_410 = fStack_6d4;
          fStack_40c = fStack_4c8;
          uStack_408 = uStack_4c4;
        }
        pfVar10 = afStack_484 + 1;
        iVar8 = 8;
        do {
          dVar12 = CDXEngine__Helper_0055dfe7((double)(pfVar10[-1] * _DAT_005d8c4c));
          lStack_68c = (longlong)ROUND(dVar12);
          iVar4 = (int)(float)lStack_68c;
          dVar12 = CDXEngine__Helper_0055dfe7((double)(*pfVar10 * _DAT_005d8c4c));
          iVar11 = iStack_678;
          lStack_68c = (longlong)ROUND(dVar12);
          if (iVar4 < iStack_6a0) {
            iStack_6a0 = iVar4;
          }
          if (iStack_698 < iVar4) {
            iStack_698 = iVar4;
          }
          if ((int)(float)lStack_68c < (int)fStack_684) {
            fStack_684 = (float)lStack_68c;
          }
          if ((int)fStack_680 < (int)(float)lStack_68c) {
            fStack_680 = (float)lStack_68c;
          }
          pfVar10 = pfVar10 + 4;
          iVar8 = iVar8 + -1;
        } while (iVar8 != 0);
        if (iStack_6a0 < 0) {
          iStack_6a0 = 0;
        }
        if (0x3f < iStack_698) {
          iStack_698 = 0x3f;
        }
        if ((int)fStack_684 < 0) {
          fStack_684 = 0.0;
        }
        if (0x3f < (int)fStack_680) {
          fStack_680 = 8.82818e-44;
        }
        if (iStack_698 < 0) {
          iStack_698 = 0;
          *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 0;
        }
        if (0x3f < iStack_6a0) {
          iStack_6a0 = 0x3f;
          *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 0;
        }
        iVar8 = iStack_6a0;
        if ((int)fStack_680 < 0) {
          fStack_680 = 0.0;
          *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 0;
        }
        if (0x3f < (int)fStack_684) {
          fStack_684 = 8.82818e-44;
          *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 0;
        }
        fVar9 = fStack_684;
        if (iStack_6a0 < iStack_640) {
          iStack_640 = iStack_6a0;
        }
        if (iStack_63c < iStack_698) {
          iStack_63c = iStack_698;
        }
        if ((int)fStack_684 < (int)fStack_634) {
          fStack_634 = fStack_684;
        }
        if ((int)fStack_638 < (int)fStack_680) {
          fStack_638 = fStack_680;
        }
        *(int *)(param_1[2] + iStack_678) = iStack_6a0;
        *(float *)(param_1[2] + 4 + iStack_678) = fStack_684;
        *(int *)(param_1[2] + 8 + iStack_678) = (iStack_698 - iStack_6a0) + 1;
        *(int *)(param_1[2] + 0xc + iStack_678) = ((int)fStack_680 - (int)fStack_684) + 1;
        *(undefined4 *)(param_1[2] + 0x18 + iStack_678) = 1;
        *(undefined4 *)(param_1[2] + 0x14 + iStack_678) = 1;
        uVar5 = OID__AllocObject(*(int *)(param_1[2] + 0xc + iStack_678) *
                                 *(int *)(param_1[2] + iStack_678 + 8) * 4,0x70,
                                 s_C__dev_ONSLAUGHT2_StaticShadows__006329f8,0x264);
        fStack_6c4 = (float)iVar8;
        *(undefined4 *)(param_1[2] + 0x10 + iVar11) = uVar5;
        if (iVar8 <= iStack_698) {
          do {
            fStack_6c0 = fVar9;
            if ((int)fVar9 <= (int)fStack_680) {
              fStack_6a8 = (float)(int)fStack_6c4 * _DAT_005d8c44;
              do {
                fVar9 = fStack_6c4;
                sprintf(acStack_114,s_Building_shadow_map_for__d__d__d_00632a30);
                DebugTrace(acStack_114);
                pvVar6 = (void *)OID__AllocObject(0x200,0x70,
                                                  s_C__dev_ONSLAUGHT2_StaticShadows__006329f8,0x26f)
                ;
                fStack_67c = 1.4013e-45;
                fStack_69c = (float)((int)fStack_6c0 - (int)fStack_684);
                lStack_68c = CONCAT44(lStack_68c._4_4_,(float)(int)fStack_6c0 * _DAT_005d8c44);
                fStack_6b8 = 0.0;
                *(void **)(*(int *)(param_1[2] + iVar11 + 0x10) +
                          ((*(int *)(param_1[2] + iVar11 + 8) * (int)fStack_69c - iStack_6a0) +
                          (int)fVar9) * 4) = pvVar6;
                do {
                  fStack_6bc = 0.0;
                  fStack_690 = 0.0;
                  fStack_694 = 0.0;
                  fStack_6a4 = (float)(int)fStack_6b8 * _DAT_005d8c4c + (float)lStack_68c;
                  do {
                    bVar1 = false;
                    fStack_5fc = fStack_6a4;
                    fStack_5f8 = 0.0;
                    fStack_600 = (float)(int)fStack_694 * _DAT_005d8c4c + fStack_6a8;
                    dVar12 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_600);
                    fStack_5f8 = (float)dVar12;
                    CMCMech__Helper_004b0fb0();
                    CUnitAI__Unk_0049bc80(auStack_164,auStack_5c0,unaff_EDI);
                    CUnitAI__Unk_0049bc10((int)auStack_5c0);
                    dVar12 = CUnitAI__Unk_0049bc40(auStack_164);
                    CUnitAI__Unk_0049bbb0(auStack_5c0,(void *)(float)dVar12,(float)unaff_EDI);
                    Vec3__SetXYZ();
                    Vec3__SetXYZ();
                    Vec3__SetXYZ();
                    Vec3__SetXYZ();
                    pvVar2 = pvStack_618;
                    iVar4 = CMeshPart__StartLineTriangleBucketSearch
                                      (pvStack_618,(int)&uStack_610,(int)auStack_184,
                                       (int)&psStack_490,unaff_EDI);
                    iVar8 = *(int *)((int)pvVar2 + 0x100);
                    pfVar10 = (float *)(iVar8 + 0x40);
                    if (iVar4 == 0) {
LAB_004edf26:
                      iVar8 = 0;
                    }
                    else {
                      do {
                        fStack_344 = (float)(int)*psStack_490 * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *pfVar10;
                        fStack_340 = (float)(int)psStack_490[1] * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *(float *)(iVar8 + 0x44);
                        fStack_33c = (float)(int)psStack_490[2] * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *(float *)(iVar8 + 0x48);
                        fStack_364 = (float)(int)*psStack_48c * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *pfVar10;
                        fStack_360 = (float)(int)psStack_48c[1] * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *(float *)(iVar8 + 0x44);
                        fStack_6c8 = (float)(int)psStack_48c[2];
                        fStack_35c = (float)(int)fStack_6c8 * *(float *)(iVar8 + 0x50) *
                                     _DAT_005d8618 + *(float *)(iVar8 + 0x48);
                        CPolyBucket__CompressedToVertex(auStack_174,pfVar10);
                        CExplosionInitThing__Helper_0040d150
                                  (auStack_404,auStack_124,(void *)0x43fa0000,(float)unaff_EDI);
                        CMeshCollisionVolume__Helper_0040d120
                                  (&uStack_610,auStack_134,extraout_EAX_00,unaff_EDI);
                        iVar4 = CStaticShadows__RayTriangleIntersect
                                          (&fStack_344,&fStack_364,auStack_174,uStack_610,uStack_60c
                                           ,uStack_608,uStack_604,*extraout_EAX_01,
                                           extraout_EAX_01[1],extraout_EAX_01[2]);
                        if (iVar4 != 0) {
                          bVar1 = true;
                        }
                        iVar4 = CMeshPart__GetNextLineTriangleFromBucketSearch
                                          (pvStack_618,(int)&psStack_490,(void *)0x0,(int)unaff_EDI)
                        ;
                      } while (iVar4 != 0);
                      if (!bVar1) goto LAB_004edf26;
                      iVar8 = 1;
                      fStack_67c = 0.0;
                    }
                    uVar7 = iVar8 << (SUB41(fStack_690,0) & 0x1f);
                    iVar8 = (int)fStack_6bc + (int)fStack_6b8 * 2;
                    if (fStack_690 == 0.0) {
                      *(uint *)((int)pvVar6 + iVar8 * 4) = uVar7;
                    }
                    else {
                      *(uint *)((int)pvVar6 + iVar8 * 4) =
                           *(uint *)((int)pvVar6 + iVar8 * 4) | uVar7;
                    }
                    fStack_690 = (float)((int)fStack_690 + 1);
                    if (fStack_690 == 4.48416e-44) {
                      fStack_690 = 0.0;
                      fStack_6bc = (float)((int)fStack_6bc + 1);
                    }
                    fStack_694 = (float)((int)fStack_694 + 1);
                  } while ((int)fStack_694 < 0x40);
                  fStack_6b8 = (float)((int)fStack_6b8 + 1);
                } while ((int)fStack_6b8 < 0x40);
                if (fStack_67c != 0.0) {
                  if (pvVar6 != (void *)0x0) {
                    OID__FreeObject(pvVar6);
                  }
                  *(undefined4 *)
                   (*(int *)(iStack_678 + param_1[2] + 0x10) +
                   ((*(int *)(iStack_678 + param_1[2] + 8) * (int)fStack_69c - iStack_6a0) +
                   (int)fStack_6c4) * 4) = 0;
                }
                fStack_6c0 = (float)((int)fStack_6c0 + 1);
                iVar11 = iStack_678;
              } while ((int)fStack_6c0 <= (int)fStack_680);
            }
            fStack_6c4 = (float)((int)fStack_6c4 + 1);
            fVar9 = fStack_684;
          } while ((int)fStack_6c4 <= iStack_698);
        }
        iVar8 = iStack_614;
        if (*(int *)(iStack_614 + 0x100) != 0) {
          CStaticShadows__CleanupHelper();
          *(undefined4 *)(iVar8 + 0x100) = 0;
        }
        *(int **)(iVar8 + 0x100) = piStack_61c;
      }
      iStack_644 = iStack_644 + 1;
    } while (iStack_644 < param_1[3]);
  }
  fVar9 = fStack_638;
  iVar8 = iStack_63c;
  DebugTrace(s_Shadow_map_done_00632a1c);
  param_1[4] = iStack_640;
  param_1[5] = (int)fStack_634;
  param_1[6] = (iVar8 - iStack_640) + 1;
  param_1[7] = ((int)fVar9 - (int)fStack_634) + 1;
  CStaticShadows__ApplyShadowsToGrid(0xffffffff,0xffffffff,0xffffffff,0xffffffff);
  ExceptionList = pvStack_14;
  return;
}
