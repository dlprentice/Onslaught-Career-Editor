/* address: 0x00501cd0 */
/* name: CVertexShader__ApplyRenderStateShaderConstants */
/* signature: void __fastcall CVertexShader__ApplyRenderStateShaderConstants(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CVertexShader__ApplyRenderStateShaderConstants(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined1 ***pppuVar4;
  int **ppiVar5;
  undefined1 *puVar6;
  undefined1 *puStack_3f0;
  undefined4 uStack_3ec;
  undefined1 *puStack_3e8;
  int *piStack_3e4;
  undefined4 uStack_3e0;
  undefined4 *puStack_3dc;
  undefined4 uStack_3d8;
  int *piStack_3d4;
  undefined4 uStack_3d0;
  undefined4 *puStack_3cc;
  undefined4 uStack_3c8;
  int *piStack_3c4;
  undefined4 uStack_3c0;
  undefined4 *puStack_3bc;
  undefined4 uStack_3b8;
  int *piStack_3b4;
  undefined4 uStack_3b0;
  undefined4 *puStack_3ac;
  undefined4 uStack_3a8;
  undefined4 *puStack_3a4;
  undefined1 *puStack_3a0;
  int *piStack_39c;
  undefined4 uStack_398;
  undefined1 **ppuStack_394;
  undefined4 uStack_390;
  int *piStack_38c;
  undefined4 uStack_388;
  undefined1 **ppuStack_384;
  undefined4 uStack_380;
  int *piStack_37c;
  undefined4 uStack_378;
  undefined1 **ppuStack_374;
  undefined4 uStack_370;
  int *piStack_36c;
  undefined4 uStack_368;
  undefined1 **ppuStack_364;
  undefined4 uStack_360;
  undefined1 **ppuStack_35c;
  undefined1 *puStack_358;
  undefined1 *puStack_354;
  undefined1 **ppuStack_350;
  undefined1 *puStack_34c;
  float *pfStack_348;
  undefined4 *puStack_344;
  undefined4 *puStack_340;
  undefined1 *puStack_33c;
  undefined1 *puStack_338;
  undefined1 *puStack_334;
  undefined1 *puStack_330;
  undefined4 uStack_32c;
  undefined1 *puStack_328;
  undefined1 *puStack_324;
  undefined4 uStack_320;
  undefined1 *puStack_2cc;
  undefined1 *puStack_2c8;
  float *pfStack_2c4;
  undefined1 auStack_2a8 [12];
  undefined4 auStack_29c [4];
  undefined1 auStack_28c [24];
  undefined1 auStack_274 [12];
  undefined1 auStack_268 [8];
  undefined1 auStack_260 [4];
  undefined4 auStack_25c [7];
  float local_240 [16];
  undefined4 local_200 [3];
  undefined1 auStack_1f4 [12];
  undefined1 auStack_1e8 [12];
  float fStack_1dc;
  undefined1 auStack_1d8 [12];
  undefined1 auStack_1cc [64];
  undefined1 auStack_18c [12];
  undefined4 local_180 [3];
  undefined1 auStack_174 [116];
  undefined1 local_100 [36];
  undefined1 auStack_dc [52];
  undefined1 auStack_a8 [168];

  if (DAT_0063c108 != '\0') {
    if (*(char *)(param_1 + 0x34) != '\0') {
      CVertexShader__ApplyCustomRenderStateShaderConstants(param_1);
      return;
    }
    pfStack_2c4 = (float *)0x501d0b;
    CDXEngine__GetProjectionWithDepthBias(&DAT_009c65c0,local_240);
    pfStack_2c4 = local_240;
    puVar2 = &DAT_009c6914;
    puVar3 = local_200;
    for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    puStack_2c8 = local_100;
    puVar2 = &DAT_009c6954;
    puVar3 = local_180;
    for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    puStack_2cc = (undefined1 *)0x501d4b;
    CTexture__Helper_005768fe();
    puStack_2cc = auStack_18c;
    CTexture__Helper_005768fe();
    CTexture__Helper_005768fe();
    CVertexShader__Helper_00576b47();
    (**(code **)(*DAT_00888a50 + 0x178))();
    (**(code **)(*DAT_00888a50 + 0x178))();
    (**(code **)(*DAT_00888a50 + 0x178))();
    uStack_320 = 0x501e31;
    CDXEngine__GetProjectionWithDepthBias(&DAT_009c65c0,&fStack_1dc);
    puVar2 = &DAT_009c6914;
    puVar3 = auStack_29c;
    for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    puVar2 = &DAT_009c6954;
    puVar3 = auStack_25c;
    for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    puStack_324 = auStack_dc;
    uStack_320 = 0;
    puStack_328 = (undefined1 *)0x501e68;
    CVertexShader__Helper_00576e0a();
    puStack_328 = auStack_2a8;
    puStack_330 = auStack_a8;
    uStack_32c = 0;
    puStack_334 = (undefined1 *)0x501e7c;
    CVertexShader__Helper_00576e0a();
    puStack_334 = auStack_274;
    puStack_338 = &stack0xfffffd4c;
    puStack_33c = auStack_174;
    puStack_340 = (undefined4 *)0x501e96;
    CTexture__Helper_005768fe();
    puStack_340 = local_200;
    puStack_344 = local_180;
    pfStack_348 = local_240;
    puStack_34c = (undefined1 *)0x501eb3;
    CTexture__Helper_005768fe();
    puStack_34c = auStack_28c;
    ppuStack_350 = &puStack_2cc;
    puStack_354 = auStack_1cc;
    puStack_358 = (undefined1 *)0x501ecd;
    CTexture__Helper_005768fe();
    puStack_358 = auStack_1d8;
    ppuStack_35c = &puStack_328;
    uStack_360 = 0x501edf;
    CVertexShader__Helper_00576b47();
    ppuStack_364 = &puStack_330;
    uStack_360 = 1;
    uStack_368 = 4;
    piStack_36c = DAT_00888a50;
    uStack_370 = 0x501ef6;
    (**(code **)(*DAT_00888a50 + 0x178))();
    ppuStack_374 = &puStack_330;
    uStack_370 = 1;
    uStack_378 = 5;
    piStack_37c = DAT_00888a50;
    uStack_380 = 0x501f0d;
    (**(code **)(*DAT_00888a50 + 0x178))();
    ppuStack_384 = &puStack_330;
    uStack_380 = 1;
    uStack_388 = 6;
    piStack_38c = DAT_00888a50;
    uStack_390 = 0x501f24;
    (**(code **)(*DAT_00888a50 + 0x178))();
    ppuStack_394 = &puStack_330;
    uStack_390 = 1;
    uStack_398 = 7;
    piStack_39c = DAT_00888a50;
    puStack_3a0 = (undefined1 *)0x501f3b;
    (**(code **)(*DAT_00888a50 + 0x178))();
    puStack_3a0 = auStack_260;
    puStack_3a4 = &uStack_370;
    uStack_3a8 = 0x501f4d;
    CVertexShader__Helper_00576b47();
    uStack_3a8 = 1;
    puStack_3ac = &uStack_378;
    uStack_3b0 = 8;
    piStack_3b4 = DAT_00888a50;
    uStack_3b8 = 0x501f64;
    (**(code **)(*DAT_00888a50 + 0x178))();
    puStack_3bc = &uStack_378;
    uStack_3b8 = 1;
    uStack_3c0 = 9;
    piStack_3c4 = DAT_00888a50;
    uStack_3c8 = 0x501f7b;
    (**(code **)(*DAT_00888a50 + 0x178))();
    puStack_3cc = &uStack_378;
    uStack_3c8 = 1;
    uStack_3d0 = 10;
    piStack_3d4 = DAT_00888a50;
    uStack_3d8 = 0x501f92;
    (**(code **)(*DAT_00888a50 + 0x178))();
    puStack_3dc = &uStack_378;
    uStack_3d8 = 1;
    uStack_3e0 = 0xb;
    piStack_3e4 = DAT_00888a50;
    puStack_3e8 = (undefined1 *)0x501fa9;
    (**(code **)(*DAT_00888a50 + 0x178))();
    puStack_3e8 = auStack_268;
    puStack_3f0 = auStack_1e8;
    uStack_3ec = 0;
    uStack_3c8 = 0;
    piStack_3c4 = (int *)0x0;
    uStack_3c0 = 0;
    CVertexShader__Helper_00576e0a();
    puVar6 = auStack_1f4;
    ppiVar5 = &piStack_3d4;
    pppuVar4 = &ppuStack_384;
    CVBufTexture__Helper_0057600b();
    (**(code **)(*DAT_00888a50 + 0x178))(DAT_00888a50,0x19,&uStack_390,1,pppuVar4,ppiVar5,puVar6);
    puStack_3f0 = _DAT_009c68b0;
    uStack_3ec = 0x402df84d;
    puStack_3e8 = (undefined1 *)0x0;
    piStack_3e4 = (int *)0x0;
    (**(code **)(*DAT_00888a50 + 0x178))(DAT_00888a50,0x1a,&puStack_3f0,1);
    stricmp((char *)(param_1 + 8),s_ShadowShader_0063cf68);
  }
  return;
}
