/* address: 0x00502920 */
/* name: CVertexShader__ApplyCustomRenderStateShaderConstants */
/* signature: void __fastcall CVertexShader__ApplyCustomRenderStateShaderConstants(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CVertexShader__ApplyCustomRenderStateShaderConstants(int param_1)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  int **ppiVar4;
  int ****ppppiVar5;
  undefined4 *puVar6;
  int ***pppiVar7;
  int *piVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  int *piVar11;
  int ***pppiStack_5a0;
  int **ppiStack_59c;
  int ***pppiStack_598;
  int **ppiStack_594;
  undefined4 ***pppuStack_590;
  int **ppiStack_58c;
  int ***pppiStack_588;
  undefined4 ***pppuStack_584;
  undefined4 ***pppuStack_580;
  int **ppiStack_578;
  int *piStack_574;
  int ***pppiStack_570;
  int **ppiStack_56c;
  int **ppiStack_568;
  int **ppiStack_564;
  undefined1 *puStack_560;
  int **ppiStack_55c;
  undefined1 *puStack_558;
  undefined1 *puStack_554;
  undefined1 *puStack_550;
  undefined1 *puStack_54c;
  int **ppiStack_548;
  int **ppiStack_544;
  int *piStack_540;
  int **ppiStack_53c;
  int *piStack_538;
  float fStack_534;
  int iVar12;
  int aiStack_51c [2];
  int **ppiStack_514;
  int **ppiStack_510;
  int **ppiStack_50c;
  int *piStack_508;
  float fStack_504;
  undefined4 uStack_500;
  float fStack_4fc;
  int **ppiStack_4f8;
  float fStack_4f4;
  int **ppiStack_4f0;
  float fStack_4ec;
  undefined4 uStack_4e8;
  undefined4 uStack_4e4;
  undefined4 uStack_4e0;
  undefined4 uStack_4dc;
  undefined4 uStack_4d8;
  int **ppiStack_4d4;
  int **ppiStack_4d0;
  int **ppiStack_4cc;
  int *piStack_4c8;
  int ***pppiStack_4c4;
  int **ppiStack_4c0;
  int **ppiStack_4bc;
  undefined1 *puStack_4b8;
  int **ppiStack_4a0;
  int **ppiStack_49c;
  undefined1 *puStack_498;
  undefined4 uStack_494;
  int **ppiStack_480;
  int **ppiStack_47c;
  undefined1 *puStack_478;
  undefined4 uStack_474;
  uint uStack_470;
  undefined4 uStack_46c;
  uint uStack_468;
  undefined4 uStack_464;
  uint uStack_460;
  undefined4 uStack_45c;
  uint uStack_458;
  undefined4 uStack_454;
  uint uStack_450;
  undefined4 uStack_44c;
  uint uStack_448;
  int *piStack_444;
  uint uStack_440;
  int *piStack_43c;
  undefined4 uStack_438;
  undefined4 uStack_434;
  undefined4 uStack_430;
  float fStack_41c;
  float fStack_418;
  float fStack_414;
  undefined4 uStack_410;
  int *piStack_40c;
  undefined4 uStack_408;
  undefined4 uStack_404;
  undefined4 uStack_400;
  undefined4 uStack_3fc;
  undefined4 uStack_3f8;
  undefined4 uStack_3f4;
  undefined4 uStack_3f0;
  undefined4 uStack_3ec;
  undefined4 uStack_3e8;
  undefined4 uStack_3e4;
  undefined4 uStack_3e0;
  undefined4 uStack_3dc;
  undefined4 uStack_3d8;
  undefined4 uStack_3d4;
  int ***pppiStack_3d0;
  int **ppiStack_3cc;
  int **ppiStack_3c8;
  int *piStack_3c4;
  int ***pppiStack_3c0;
  int *piStack_3bc;
  int **appiStack_3b8 [3];
  int *apiStack_3ac [6];
  int *apiStack_394 [2];
  undefined1 auStack_38c [92];
  undefined1 auStack_330 [24];
  undefined1 auStack_318 [4];
  int *apiStack_314 [2];
  int *apiStack_30c [3];
  undefined4 local_300 [11];
  int *apiStack_2d4 [2];
  undefined1 auStack_2cc [64];
  int *apiStack_28c [3];
  int aiStack_280 [13];
  int *apiStack_24c [3];
  undefined1 local_240 [28];
  undefined1 auStack_224 [36];
  float local_200 [4];
  undefined1 auStack_1f0 [24];
  int *apiStack_1d8 [3];
  int *apiStack_1cc [3];
  undefined4 local_1c0 [4];
  int *apiStack_1b0 [9];
  int *apiStack_18c [13];
  int *apiStack_158 [3];
  int *apiStack_14c [12];
  int *apiStack_11c [14];
  int *apiStack_e4 [16];
  undefined1 auStack_a4 [12];
  undefined1 auStack_98 [76];
  int *apiStack_4c [19];

  fStack_534 = 7.361633e-39;
  CDXEngine__GetProjectionWithDepthBias(&DAT_009c65c0,local_200);
  piStack_538 = (int *)local_240;
  puVar6 = &DAT_009c6914;
  puVar9 = local_300;
  for (iVar3 = 0x10; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar9 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar9 = puVar9 + 1;
  }
  puVar6 = &DAT_009c6954;
  puVar9 = local_1c0;
  for (iVar3 = 0x10; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar9 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar9 = puVar9 + 1;
  }
  fStack_534 = 0.0;
  ppiStack_53c = (int **)0x50297b;
  CVertexShader__Helper_00576e0a();
  ppiStack_53c = apiStack_30c;
  ppiStack_544 = apiStack_4c;
  piStack_540 = (int *)0x0;
  ppiStack_548 = (int **)0x502991;
  CVertexShader__Helper_00576e0a();
  ppiStack_548 = apiStack_1d8;
  puStack_54c = auStack_318;
  puStack_550 = auStack_98;
  puStack_554 = (undefined1 *)0x5029ae;
  CTexture__Helper_005768fe();
  puStack_554 = auStack_224;
  puStack_558 = auStack_a4;
  ppiStack_55c = apiStack_e4;
  puStack_560 = (undefined1 *)0x5029cb;
  CTexture__Helper_005768fe();
  puStack_560 = auStack_1f0;
  ppiStack_564 = (int **)auStack_330;
  ppiStack_568 = apiStack_1b0;
  ppiStack_56c = (int **)0x5029e8;
  CTexture__Helper_005768fe();
  ppiStack_56c = (int **)0x1;
  ppiStack_55c = (int **)0x0;
  puStack_558 = (undefined1 *)0x3f800000;
  puStack_554 = (undefined1 *)0x3f000000;
  puStack_550 = (undefined1 *)0x40000000;
  piStack_574 = (int *)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634420 * 4);
  ppiStack_578 = (int **)DAT_00888a50;
  pppiStack_570 = &ppiStack_55c;
  (*(code *)(*DAT_00888a50)[0x5e])();
  piVar8 = *(int **)(param_1 + 0x38);
  puStack_558 = (undefined1 *)0x0;
  iVar3 = *piVar8;
  if (iVar3 != 0) {
    puStack_54c = (undefined1 *)0x0;
    puStack_550 = (undefined1 *)0x0;
    fStack_534 = 0.0;
    iVar12 = 0;
    do {
      piStack_538 = piVar8;
      if (iVar3 == DAT_00634264) {
        pppuStack_580 = (undefined4 ***)apiStack_1cc;
        pppuStack_584 = (undefined4 ***)apiStack_30c;
        pppiStack_588 = (int ***)0x502a6f;
        CVertexShader__Helper_00576b47();
        ppiStack_58c = apiStack_314;
        pppiStack_588 = (int ***)0x1;
        pppuStack_590 = (undefined4 ***)**(float **)(*(int *)(param_1 + 0x40) + DAT_0063433c * 4);
        ppiStack_594 = (int **)DAT_00888a50;
        pppiStack_598 = (int ***)0x502a96;
        (*(code *)(*DAT_00888a50)[0x5e])();
        ppiStack_59c = apiStack_314;
        pppiStack_598 = (int ***)0x1;
        pppiStack_5a0 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634348 * 4);
        (*(code *)(*DAT_00888a50)[0x5e])(DAT_00888a50);
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634354 * 4),
                   apiStack_314,1);
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634360 * 4),
                   apiStack_314,1);
      }
      if (*piVar8 == DAT_00634270) {
        pppuStack_580 = (undefined4 ***)apiStack_24c;
        pppuStack_584 = (undefined4 ***)auStack_38c;
        pppiStack_588 = (int ***)0x502b30;
        CVertexShader__Helper_00576b47();
        ppiStack_58c = apiStack_394;
        pppiStack_588 = (int ***)0x1;
        pppuStack_590 = (undefined4 ***)**(float **)(*(int *)(param_1 + 0x40) + DAT_00634468 * 4);
        ppiStack_594 = (int **)DAT_00888a50;
        pppiStack_598 = (int ***)0x502b57;
        (*(code *)(*DAT_00888a50)[0x5e])();
        ppiStack_59c = apiStack_394;
        pppiStack_598 = (int ***)0x1;
        pppiStack_5a0 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634474 * 4);
        (*(code *)(*DAT_00888a50)[0x5e])(DAT_00888a50);
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634480 * 4),
                   apiStack_394,1);
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_0063448c * 4),
                   apiStack_394,1);
      }
      if (*piVar8 == DAT_0063430c) {
        ppiStack_480 = (int **)DAT_009c68b8;
        puStack_478 = DAT_009c68c0;
        uStack_474 = DAT_009c68c4;
        pppuStack_580 = (undefined4 ***)0x1;
        ppiStack_564 = (int **)DAT_009c68c0;
        pppuStack_584 = &ppiStack_56c;
        ppiStack_47c = (int **)DAT_009c68bc;
        ppiStack_56c = (int **)DAT_009c68b8;
        ppiStack_568 = (int **)DAT_009c68bc;
        puStack_560 = (undefined1 *)0x3f800000;
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634510 * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x502c5c;
        (*(code *)(*DAT_00888a50)[0x5e])();
        pppuStack_590 = (undefined4 ***)apiStack_11c;
        ppiStack_594 = &piStack_43c;
        pppiStack_598 = (int ***)apiStack_3ac;
        piStack_43c = (int *)0x0;
        uStack_438 = 0;
        uStack_434 = 0;
        uStack_430 = 0x3f800000;
        ppiStack_59c = (int **)0x502ca5;
        CVertexShader__Helper_005766a5();
        pppiStack_5a0 = appiStack_3b8;
        ppiStack_59c = (int **)0x1;
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634504 * 4));
      }
      if (*piVar8 == DAT_00634318) {
        uStack_44c = 0;
        ppiStack_55c = (int **)((float)DAT_009c68e0 * _DAT_005df8fc);
        uStack_450 = DAT_009c68e4 >> 0x10 & 0xff;
        uStack_464 = 0;
        uStack_468 = DAT_009c68e4 >> 8 & 0xff;
        uStack_440 = DAT_009c68e4 & 0xff;
        piStack_43c = (int *)0x0;
        piStack_444 = (int *)0x0;
        uStack_448 = DAT_009c68e4 >> 0x18;
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        ppiStack_56c = (int **)((float)ppiStack_55c * (float)uStack_450 * _DAT_005df8fc);
        ppiStack_568 = (int **)((float)ppiStack_55c * (float)uStack_468 * _DAT_005df8fc);
        ppiStack_564 = (int **)((float)ppiStack_55c * (float)uStack_440 * _DAT_005df8fc);
        puStack_560 = (undefined1 *)((float)ppiStack_55c * (float)uStack_448 * _DAT_005df8fc);
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634528 * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x502ddd;
        (*(code *)(*DAT_00888a50)[0x5e])();
        ppiStack_594 = (int **)&stack0xfffffa84;
        pppuStack_590 = (undefined4 ***)0x1;
        ppiStack_578 = (int **)0x0;
        piStack_574 = (int *)0x0;
        pppiStack_570 = (int ***)0x0;
        pppiStack_598 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_0063451c * 4);
        ppiStack_59c = (int **)DAT_00888a50;
        pppiStack_5a0 = (int ***)0x502e27;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_00634300) {
        ppiStack_49c = (int **)DAT_009c68f0;
        puStack_498 = DAT_009c68f4;
        ppiStack_4a0 = (int **)DAT_009c68ec;
        ppiStack_568 = (int **)DAT_009c68f0;
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        uStack_494 = DAT_009c68f8;
        ppiStack_56c = (int **)DAT_009c68ec;
        ppiStack_564 = (int **)DAT_009c68f4;
        puStack_560 = (undefined1 *)0x0;
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_006344f8 * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x502eb1;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_00634324) {
        pppuStack_584 = (undefined4 ***)&piStack_40c;
        pppuStack_580 = (undefined4 ***)0x1;
        piStack_40c = (int *)0x3eaaaaab;
        uStack_408 = 0;
        uStack_404 = 0;
        uStack_400 = 0;
        uStack_3fc = 0;
        uStack_3f8 = 0x3eaaaaab;
        uStack_3f4 = 0;
        uStack_3f0 = 0;
        uStack_3ec = 0;
        uStack_3e8 = 0;
        uStack_3e4 = 0x3eaaaaab;
        uStack_3e0 = 0;
        uStack_3dc = 0;
        uStack_3d8 = 0;
        uStack_3d4 = 0;
        pppiStack_3d0 = (int ***)0x3eaaaaab;
        pppiStack_588 = (int ***)0x7;
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x502f8b;
        (*(code *)(*DAT_00888a50)[0x5e])();
        ppiStack_594 = &piStack_40c;
        pppuStack_590 = (undefined4 ***)0x1;
        pppiStack_598 = (int ***)0x8;
        ppiStack_59c = (int **)DAT_00888a50;
        pppiStack_5a0 = (int ***)0x502fa5;
        (*(code *)(*DAT_00888a50)[0x5e])();
        pppiStack_5a0 = (int ***)0x1;
        (*(code *)(*DAT_00888a50)[0x5e])(DAT_00888a50,9,&piStack_40c);
        puStack_554 = (undefined1 *)0x0;
        if (0 < DAT_009c68cc) {
          ppppiVar5 = (int ****)0xb;
          ppiStack_55c = (int **)&DAT_009c69d4;
          do {
            pppuStack_580 = (undefined4 ***)apiStack_18c;
            pppiVar7 = (int ***)ppiStack_55c;
            ppiVar4 = apiStack_18c;
            for (iVar3 = 0x10; iVar3 != 0; iVar3 = iVar3 + -1) {
              *ppiVar4 = (int *)*pppiVar7;
              pppiVar7 = pppiVar7 + 1;
              ppiVar4 = ppiVar4 + 1;
            }
            pppuStack_584 = (undefined4 ***)auStack_2cc;
            pppiStack_588 = (int ***)0x503004;
            CVertexShader__Helper_00576b47();
            ppiStack_58c = apiStack_2d4;
            pppiStack_588 = (int ***)0x1;
            pppuStack_590 = (undefined4 ***)((int)ppppiVar5 + -1);
            ppiStack_594 = (int **)DAT_00888a50;
            pppiStack_598 = (int ***)0x503020;
            (*(code *)(*DAT_00888a50)[0x5e])();
            ppiStack_59c = apiStack_2d4;
            pppiStack_598 = (int ***)0x1;
            pppiStack_5a0 = (int ***)ppppiVar5;
            (*(code *)(*DAT_00888a50)[0x5e])(DAT_00888a50);
            (*(code *)(*DAT_00888a50)[0x5e])
                      (DAT_00888a50,(undefined1 *)((int)ppppiVar5 + 1),apiStack_2d4,1);
            puStack_554 = (undefined1 *)((int)puStack_554 + 1);
            ppiStack_55c = ppiStack_55c + 0x10;
            ppppiVar5 = (int ****)((int)ppppiVar5 + 3);
            piVar8 = piStack_538;
          } while ((int)puStack_554 < DAT_009c68cc);
        }
      }
      if ((*piVar8 == DAT_006342c4) || (*piVar8 == DAT_00634210)) {
        uStack_46c = 0;
        uStack_470 = DAT_009c68a8 >> 0x10 & 0xff;
        uStack_45c = 0;
        uStack_458 = DAT_009c68a8 & 0xff;
        uStack_460 = DAT_009c68a8 >> 8 & 0xff;
        ppiStack_56c = (int **)((float)uStack_470 * _DAT_005df8fc);
        uStack_454 = 0;
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        puStack_560 = (undefined1 *)0x3f800000;
        ppiStack_568 = (int **)((float)uStack_460 * _DAT_005df8fc);
        ppiStack_564 = (int **)((float)uStack_458 * _DAT_005df8fc);
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_0063445c * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x503141;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_00634114) {
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        ppiStack_56c = (int **)0x0;
        ppiStack_568 = (int **)0x0;
        ppiStack_564 = (int **)0x0;
        puStack_560 = (undefined1 *)0x41f00000;
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_006343cc * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x503190;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_00634330) {
        puStack_554 = (undefined1 *)
                      SQRT(DAT_00660198 * DAT_00660198 + DAT_0066019c * DAT_0066019c + _DAT_005d8568
                          );
        fStack_41c = DAT_00660198;
        fStack_418 = DAT_0066019c;
        fStack_414 = _DAT_005d8568;
        if ((float)puStack_554 != _DAT_005d856c) {
          fStack_414 = _DAT_005d8568 / (float)puStack_554;
          fStack_41c = fStack_414 * DAT_00660198;
          fStack_418 = fStack_414 * DAT_0066019c;
        }
        fStack_41c = -fStack_41c;
        fStack_418 = -fStack_418;
        pppuStack_580 = (undefined4 ***)apiStack_28c;
        pppuStack_584 = (undefined4 ***)&fStack_41c;
        pppiStack_588 = (int ***)&piStack_3bc;
        fStack_414 = -fStack_414;
        uStack_410 = 0;
        ppiStack_58c = (int **)0x503263;
        CVertexShader__Helper_005766a5();
        pppiStack_570 = pppiStack_3c0;
        pppuStack_590 = &ppiStack_578;
        ppiStack_58c = (int **)0x1;
        ppiStack_578 = ppiStack_3c8;
        piStack_574 = piStack_3c4;
        ppiStack_56c = (int **)0x3f800000;
        ppiStack_594 = (int **)**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_0063454c * 4);
        pppiStack_598 = DAT_00888a50;
        ppiStack_59c = (int **)0x5032b0;
        (*(code *)(*DAT_00888a50)[0x5e])();
        pppiStack_5a0 = (int ***)&pppiStack_588;
        ppiStack_59c = (int **)0x1;
        pppiStack_588 = (int ***)0x40800000;
        pppuStack_584 = (undefined4 ***)0x0;
        pppuStack_580 = (undefined4 ***)0x0;
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634534 * 4));
        pppiStack_598 = (int ***)0x3f4ccccd;
        ppiStack_594 = (int **)0x3f4ccccd;
        pppuStack_590 = (undefined4 ***)0x3f4ccccd;
        ppiStack_58c = (int **)0x3f800000;
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_00634540 * 4),
                   &pppiStack_598,1);
      }
      iVar3 = *piVar8;
      if (((iVar3 == DAT_0063418c) || (iVar3 == DAT_00634198)) || (iVar3 == DAT_006341a4)) {
        cVar2 = (&DAT_009c68a0)[(int)puStack_558];
        puVar10 = puStack_558;
        while (cVar2 == '\0') {
          pcVar1 = &DAT_009c68a1 + (int)puVar10;
          puVar10 = (undefined1 *)((int)puVar10 + 1);
          cVar2 = *pcVar1;
        }
        pppuStack_580 = (undefined4 ***)0x0;
        pppuStack_584 = (undefined4 ***)0x0;
        pppiStack_588 = (int ***)0x0;
        aiStack_51c[0] = 0;
        piStack_508 = (int *)0x0;
        fStack_504 = 0.0;
        uStack_500 = 0;
        ppiStack_4f8 = (int **)0x0;
        fStack_4f4 = 0.0;
        ppiStack_4f0 = (int **)0x0;
        fStack_4ec = 0.0;
        aiStack_51c[1] = 0;
        ppiStack_514 = (int **)0x0;
        ppiStack_510 = (int **)0x0;
        uStack_4e8 = 0;
        uStack_4e4 = 0;
        uStack_4e0 = 0;
        uStack_4dc = 0;
        uStack_4d8 = 0;
        ppiStack_4d4 = (int **)0x0;
        ppiStack_58c = (int **)0x50342f;
        puStack_558 = puVar10;
        CDXEngine__Helper_0044a5f0();
        pppuStack_580 = (undefined4 ***)0x1;
        puStack_560 = (undefined1 *)0x3f800000;
        piVar8 = &DAT_009c65c0 + (int)puVar10 * 0x17;
        piVar11 = aiStack_51c;
        for (iVar3 = 0x17; iVar3 != 0; iVar3 = iVar3 + -1) {
          *piVar11 = *piVar8;
          piVar8 = piVar8 + 1;
          piVar11 = piVar11 + 1;
        }
        ppiStack_564 = ppiStack_4f0;
        pppuStack_584 = &ppiStack_56c;
        ppiStack_56c = ppiStack_4f8;
        ppiStack_568 = (int **)fStack_4f4;
        pppiStack_588 = *(int ****)(*(int *)(*(int *)(param_1 + 0x40) + DAT_006343f0 * 4) + iVar12);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x50349b;
        (*(code *)(*DAT_00888a50)[0x5e])();
        if ((int ***)ppiStack_510 == (int ***)0x0) {
LAB_005034cf:
          ppiStack_53c = (int **)-fStack_4fc;
          piStack_538 = (int *)-(float)ppiStack_4f8;
          fStack_534 = -fStack_4f4;
          iVar12 = 0;
        }
        else if ((int ***)ppiStack_510 == (int ***)0x1) {
          ppiStack_53c = ppiStack_50c;
          piStack_538 = piStack_508;
          fStack_534 = fStack_504;
          iVar12 = 0x3f800000;
        }
        else if ((int ***)ppiStack_510 == (int ***)0x2) goto LAB_005034cf;
        piStack_574 = aiStack_280;
        ppiStack_578 = (int **)&ppiStack_53c;
        pppuStack_580 = (undefined4 ***)0x50350f;
        CVertexShader__Helper_005766a5();
        ppiStack_56c = ppiStack_4c0;
        ppiStack_568 = ppiStack_4bc;
        ppiStack_564 = (int **)puStack_4b8;
        puStack_560 = (undefined1 *)0x3f800000;
        if (aiStack_51c[0] == 0) {
          ppiVar4 = *DAT_00888a50;
          iVar3 = *(int *)(*(int *)(param_1 + 0x40) + DAT_00634390 * 4);
          puVar10 = (undefined1 *)fStack_534;
LAB_005035ac:
          pppuStack_584 = &ppiStack_56c;
          pppuStack_580 = (undefined4 ***)0x1;
          pppiStack_588 = *(int ****)(iVar3 + (int)puVar10);
          ppiStack_58c = (int **)DAT_00888a50;
          pppuStack_590 = (undefined4 ***)0x5035b7;
          (*(code *)ppiVar4[0x5e])();
          if (aiStack_51c[0] == 2) {
            ppiStack_548 = ppiStack_4d0;
            ppiStack_544 = ppiStack_4cc;
            pppuStack_580 = (undefined4 ***)apiStack_28c;
            piStack_540 = piStack_4c8;
            pppuStack_584 = &ppiStack_548;
            pppiStack_588 = &ppiStack_4c0;
            ppiStack_53c = (int **)0x0;
            ppiStack_58c = (int **)0x503607;
            CVertexShader__Helper_005766a5();
            ppiVar4 = ppiStack_55c;
            pppiStack_570 = pppiStack_4c4;
            pppuStack_590 = &ppiStack_578;
            ppiStack_58c = (int **)0x1;
            ppiStack_578 = ppiStack_4cc;
            piStack_574 = piStack_4c8;
            ppiStack_56c = (int **)0x3f800000;
            ppiStack_594 = *(int ***)(*(int *)(*(int *)(param_1 + 0x40) + DAT_00634414 * 4) +
                                     (int)ppiStack_55c);
            pppiStack_598 = DAT_00888a50;
            ppiStack_59c = (int **)0x503659;
            (*(code *)(*DAT_00888a50)[0x5e])();
            pppuStack_580 = (undefined4 ***)ppiStack_4f0;
            pppiStack_5a0 = (int ***)&pppiStack_588;
            ppiStack_59c = (int **)0x1;
            pppiStack_588 = (int ***)ppiStack_4f8;
            pppuStack_584 = (undefined4 ***)fStack_4f4;
            (*(code *)(*DAT_00888a50)[0x5e])
                      (DAT_00888a50,
                       *(undefined4 *)
                        (*(int *)(*(int *)(param_1 + 0x40) + DAT_0063442c * 4) + (int)ppiVar4));
            pppuStack_590 = (undefined4 ***)ppiStack_50c;
            pppiStack_598 = (int ***)ppiStack_514;
            ppiStack_594 = ppiStack_510;
            ppiStack_58c = (int **)0x3f800000;
            (*(code *)(*DAT_00888a50)[0x5e])
                      (DAT_00888a50,
                       *(undefined4 *)
                        (*(int *)(*(int *)(param_1 + 0x40) + DAT_00634438 * 4) + (int)ppiVar4),
                       &pppiStack_598,1);
          }
        }
        else {
          if (aiStack_51c[0] == 1) {
            ppiVar4 = *DAT_00888a50;
            iVar3 = *(int *)(*(int *)(param_1 + 0x40) + DAT_0063439c * 4);
            puVar10 = puStack_54c;
            goto LAB_005035ac;
          }
          if (aiStack_51c[0] == 2) {
            ppiVar4 = *DAT_00888a50;
            iVar3 = *(int *)(*(int *)(param_1 + 0x40) + DAT_00634444 * 4);
            puVar10 = puStack_550;
            goto LAB_005035ac;
          }
        }
        if (aiStack_51c[0] == 1) {
          pppuStack_584 = &ppiStack_56c;
          pppuStack_580 = (undefined4 ***)0x1;
          ppiStack_568 = (int **)0x0;
          ppiStack_564 = (int **)0x0;
          ppiStack_56c = (int **)(_DAT_005d8568 / (fStack_4ec * fStack_4ec * _DAT_005d8578));
          puStack_560 = (undefined1 *)0x0;
          pppiStack_588 =
               *(int ****)(*(int *)(*(int *)(param_1 + 0x40) + DAT_006343a8 * 4) + (int)puStack_54c)
          ;
          ppiStack_58c = (int **)DAT_00888a50;
          pppuStack_590 = (undefined4 ***)0x50375d;
          (*(code *)(*DAT_00888a50)[0x5e])();
        }
        if (aiStack_51c[0] == 0) {
          fStack_534 = (float)((int)fStack_534 + 4);
        }
        else if (aiStack_51c[0] == 1) {
          puStack_54c = (undefined1 *)((int)puStack_54c + 4);
        }
        else if (aiStack_51c[0] == 2) {
          puStack_550 = (undefined1 *)((int)puStack_550 + 4);
        }
        puStack_558 = (undefined1 *)((int)puStack_558 + 1);
        iVar12 = iVar12 + 4;
        piVar8 = piStack_538;
      }
      if (*piVar8 == DAT_00634174) {
        pppuStack_580 = (undefined4 ***)apiStack_1cc;
        pppiStack_588 = (int ***)apiStack_14c;
        pppuStack_584 = (undefined4 ***)0x0;
        uStack_438 = 0;
        uStack_434 = 0;
        uStack_430 = 0;
        ppiStack_58c = (int **)0x5037df;
        CVertexShader__Helper_00576e0a();
        ppiStack_58c = apiStack_158;
        pppuStack_590 = (undefined4 ***)&piStack_444;
        ppiStack_594 = (int **)appiStack_3b8;
        pppiStack_598 = (int ***)0x5037fc;
        CVBufTexture__Helper_0057600b();
        ppiStack_59c = &piStack_3c4;
        pppiStack_598 = (int ***)0x1;
        pppiStack_5a0 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_00634408 * 4);
        (*(code *)(*DAT_00888a50)[0x5e])(DAT_00888a50);
      }
      if (*piVar8 == DAT_00634294) {
        ppiStack_56c = (int **)_DAT_009c73dc;
        ppiStack_568 = (int **)_DAT_009c73e0;
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        ppiStack_564 = (int **)(_DAT_005d8568 / ((float)_DAT_009c73e0 - (float)_DAT_009c73dc));
        puStack_560 = (undefined1 *)0x437f0000;
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_006344bc * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x50387d;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_006342a0) {
        pppuStack_584 = &ppiStack_56c;
        pppuStack_580 = (undefined4 ***)0x1;
        ppiStack_56c = (int **)_DAT_009c68b0;
        ppiStack_568 = (int **)0x402df84d;
        ppiStack_564 = (int **)0x0;
        puStack_560 = (undefined1 *)0x0;
        pppiStack_588 = (int ***)**(int **)(*(int *)(param_1 + 0x40) + DAT_006344bc * 4);
        ppiStack_58c = (int **)DAT_00888a50;
        pppuStack_590 = (undefined4 ***)0x5038cf;
        (*(code *)(*DAT_00888a50)[0x5e])();
      }
      if (*piVar8 == DAT_006342f4) {
        pppuStack_580 = &ppiStack_3cc;
        pppuStack_584 = (undefined4 ***)0x5038f8;
        (*(code *)**(undefined4 **)(&DAT_0089c9a4)[DAT_0089ce4c])();
        ppiStack_56c = ppiStack_3cc;
        pppiStack_588 = (int ***)&pppiStack_570;
        pppuStack_584 = (undefined4 ***)0x1;
        pppiStack_570 = pppiStack_3d0;
        ppiStack_568 = ppiStack_3c8;
        ppiStack_564 = (int **)0x0;
        ppiStack_58c = (int **)**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_006344c8 * 4);
        pppuStack_590 = DAT_00888a50;
        ppiStack_594 = (int **)0x503945;
        (*(code *)(*DAT_00888a50)[0x5e])();
        if ((g_MeshQualityDistance < _DAT_005d85cc) || (DAT_0083cd58 != '\0')) {
          pppuStack_580 = (undefined4 ***)0x0;
        }
        else {
          pppuStack_580 =
               (undefined4 ***)
               ((g_MeshQualityDistance - _DAT_005d85cc) * (g_MeshQualityDistance - _DAT_005d85cc));
        }
        pppiStack_598 = (int ***)&pppuStack_580;
        ppiStack_594 = (int **)0x1;
        ppiStack_59c = (int **)**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_006344d4 * 4);
        pppiStack_5a0 = DAT_00888a50;
        (*(code *)(*DAT_00888a50)[0x5e])();
        ppiStack_4d0 = (int **)DAT_009c73f8;
        ppiStack_4cc = (int **)DAT_009c73fc;
        ppiStack_4d4 = (int **)DAT_009c73f4;
        ppiStack_58c = (int **)DAT_009c73f8;
        piStack_4c8 = (int *)DAT_009c7400;
        pppuStack_590 = DAT_009c73f4;
        pppiStack_588 = DAT_009c73fc;
        pppuStack_584 = (undefined4 ***)0x0;
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_006344e0 * 4),
                   &pppuStack_590,1);
        ppiStack_4c0 = (int **)DAT_009c7408;
        ppiStack_4bc = (int **)DAT_009c740c;
        pppiStack_4c4 = (int ***)DAT_009c7404;
        ppiStack_59c = (int **)DAT_009c7408;
        puStack_4b8 = DAT_009c7410;
        pppiStack_5a0 = (int ***)DAT_009c7404;
        pppiStack_598 = DAT_009c740c;
        ppiStack_594 = (int **)0x0;
        (*(code *)(*DAT_00888a50)[0x5e])
                  (DAT_00888a50,**(undefined4 **)(*(int *)(param_1 + 0x40) + DAT_006344ec * 4),
                   &pppiStack_5a0,1);
      }
      iVar3 = piVar8[1];
      piVar8 = piVar8 + 1;
    } while (iVar3 != 0);
  }
  return;
}
