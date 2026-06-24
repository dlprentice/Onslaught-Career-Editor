/* address: 0x00484340 */
/* name: CExplosionInitThing__RenderTargetMarkers3D */
/* signature: void __fastcall CExplosionInitThing__RenderTargetMarkers3D(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__RenderTargetMarkers3D(int param_1)

{
  longlong lVar1;
  int iVar2;
  void *this;
  bool bVar3;
  float *pfVar4;
  int iVar5;
  float fVar6;
  undefined4 *puVar7;
  int iVar8;
  void *unaff_EDI;
  undefined4 *puVar9;
  int iVar10;
  float fVar11;
  float10 fVar12;
  float10 fVar13;
  double dVar14;
  float fVar15;
  float p10;
  float fVar16;
  float p12;
  float p13;
  float p14;
  float p15;
  longlong local_30 [2];
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;

  CExplosionInitThing__SetupOverlayMarkerRenderState();
  CExplosionInitThing__Helper_0053cd30
            (*(void **)(param_1 + 0x60),*(void **)(param_1 + 0x50),unaff_EDI);
  puVar7 = (undefined4 *)(&DAT_0089d4a0 + *(int *)(param_1 + 0x58) * 0x40);
  puVar9 = &DAT_009c6914;
  for (iVar5 = 0x10; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73e8 = 1;
  puVar7 = (undefined4 *)(&DAT_0089d520 + *(int *)(param_1 + 0x58) * 0x40);
  puVar9 = &DAT_009c6954;
  for (iVar5 = 0x10; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73e9 = 1;
  puVar7 = (undefined4 *)(&DAT_0089d5a0 + *(int *)(param_1 + 0x58) * 0x40);
  puVar9 = &DAT_009c6994;
  for (iVar5 = 0x10; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73ea = 1;
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  if (*(int *)((int)*(void **)(param_1 + 0x50) + 0x4fc) != 0) {
    pfVar4 = CExplosionInitThing__BuildInterpolatedWorldTransform
                       (*(void **)(param_1 + 0x50),(int)local_30,unaff_EDI);
    local_20 = *pfVar4;
    local_1c = pfVar4[1];
    local_18 = pfVar4[2];
    local_14 = pfVar4[3];
    CDXEngine__PushTransformState
              (&DAT_009c65c0,(int)&local_10,(int)&local_20,*(float **)(param_1 + 0x54));
    CVBufTexture__DrawSpriteEx
              (local_10,local_c,0.01,*(void **)(param_1 + 0x110),4,0,1.0,0.0,-NAN,1.0,1.0,0.0,1.0,
               0.0,1.0);
  }
  iVar8 = 0;
  pfVar4 = CExplosionInitThing__BuildInterpolatedViewpointTransform
                     (*(void **)(param_1 + 0x50),(int)local_30,unaff_EDI);
  local_20 = *pfVar4;
  local_1c = pfVar4[1];
  local_18 = pfVar4[2];
  local_14 = pfVar4[3];
  CDXEngine__PushTransformState
            (&DAT_009c65c0,(int)&local_10,(int)&local_20,*(float **)(param_1 + 0x54));
  iVar5 = *(int *)(param_1 + 0x50);
  iVar10 = *(int *)(iVar5 + 0x4e0);
  if ((iVar10 == 0) || (*(int *)(iVar5 + 0x4fc) != 0)) {
    iVar2 = *(int *)(iVar5 + 0x4cc);
    if ((iVar2 == 0) || ((*(byte *)(iVar2 + 0x34) & 0x10) == 0)) goto LAB_004844ef;
    iVar2 = *(int *)(iVar2 + 0x138);
    if (*(int *)(iVar5 + 0x138) == 0) {
      if (iVar2 == 0) {
        iVar8 = 1;
        goto LAB_004844ef;
      }
      if (iVar2 != 1) goto LAB_004844ef;
    }
    else {
      if (*(int *)(iVar5 + 0x138) != 1) goto LAB_004844ef;
      if (iVar2 == 1) {
        iVar8 = 1;
        goto LAB_004844ef;
      }
      if (iVar2 != 0) goto LAB_004844ef;
    }
  }
  iVar8 = 2;
LAB_004844ef:
  if (iVar10 == 0) {
    iVar10 = *(int *)(iVar5 + 0x4c8);
  }
  if (((*(int *)(iVar5 + 0x4fc) == 0) && (iVar10 != 0)) && (iVar8 == 2)) {
    bVar3 = true;
  }
  else {
    bVar3 = false;
  }
  if (iVar8 == 0) {
    pfVar4 = (float *)(param_1 + 0xd4 + *(int *)(param_1 + 0x58) * 4);
    fVar16 = (_DAT_005d8568 - *(float *)(param_1 + 0xd4 + *(int *)(param_1 + 0x58) * 4)) *
             DAT_008a9e20 * _DAT_005d85ec + *pfVar4;
    *pfVar4 = fVar16;
    if (ABS(_DAT_005d8568 - fVar16) < _DAT_005d8578) {
      *pfVar4 = 1.0;
    }
  }
  else if (iVar8 == 1) {
    pfVar4 = (float *)(param_1 + 0xd4 + *(int *)(param_1 + 0x58) * 4);
    fVar16 = (_DAT_005d85bc - *(float *)(param_1 + 0xd4 + *(int *)(param_1 + 0x58) * 4)) *
             DAT_008a9e20 * _DAT_005d85ec + *pfVar4;
    *pfVar4 = fVar16;
    if (ABS(_DAT_005d85bc - fVar16) < _DAT_005d8578) {
      *pfVar4 = 4.0;
    }
  }
  else if (iVar8 == 2) {
    pfVar4 = (float *)(param_1 + 0xd4 + *(int *)(param_1 + 0x58) * 4);
    fVar16 = -*pfVar4 * DAT_008a9e20 * _DAT_005d85ec + *pfVar4;
    *pfVar4 = fVar16;
    if (ABS(-fVar16) < _DAT_005d8578) {
      *pfVar4 = 0.0;
    }
  }
  fVar16 = DAT_008a9e20 * _DAT_005d85ec * _DAT_005d8bb8;
  if (bVar3) {
    pfVar4 = (float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4);
    fVar16 = (_DAT_005d85ec - *(float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4)) * fVar16 +
             *pfVar4;
    *pfVar4 = fVar16;
    if (ABS(_DAT_005d85ec - fVar16) < _DAT_005d8574) {
      *pfVar4 = 0.5;
    }
  }
  else {
    pfVar4 = (float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4);
    fVar16 = (_DAT_005d8568 - *(float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4)) * fVar16 +
             *pfVar4;
    *pfVar4 = fVar16;
    if (ABS(_DAT_005d8568 - fVar16) < _DAT_005d8574) {
      *pfVar4 = 1.0;
    }
  }
  iVar5 = *(int *)(param_1 + 0x58);
  if (_DAT_005d8568 <= *(float *)(param_1 + 0xd4 + iVar5 * 4)) {
    fVar16 = (_DAT_005d85bc - *(float *)(param_1 + 0xd4 + iVar5 * 4)) * _DAT_005d8608;
    fVar6 = _DAT_005d8568 - fVar16;
    local_30[0]._0_4_ = (int)(longlong)ROUND(fVar6 * _DAT_005db5e8 + fVar16 * _DAT_005db5e8);
    iVar10 = (int)local_30[0] * 0x10000;
    local_30[0]._0_4_ = (int)(longlong)ROUND(fVar6 * _DAT_005d8c70 + fVar16 * _DAT_005d8c70);
    iVar8 = (iVar10 + (int)local_30[0]) * 0x100;
    local_30[0] = (longlong)ROUND(fVar6 * _DAT_005dbe64 + fVar16 * _DAT_005d8c70);
    iVar10 = (int)local_30[0] << 0x10;
  }
  else {
    fVar16 = *(float *)(param_1 + 0xd4 + iVar5 * 4);
    fVar6 = _DAT_005d8568 - fVar16;
    local_30[0]._0_4_ = (int)(longlong)ROUND(fVar6 * _DAT_005db5e8 + fVar16 * _DAT_005db5e8);
    iVar10 = (int)local_30[0] * 0x100;
    local_30[0]._0_4_ = (int)(longlong)ROUND(fVar6 * _DAT_005d8c70 + fVar16 * _DAT_005d8c70);
    iVar8 = (iVar10 + (int)local_30[0]) * 0x10000;
    local_30[0] = (longlong)ROUND(fVar6 * _DAT_005dbc4c + fVar16 * _DAT_005d8c70);
    iVar10 = (int)local_30[0] << 8;
  }
  fVar11 = (float)(iVar8 + iVar10 + (int)local_30[0]);
  fVar16 = *(float *)(param_1 + 0xd4 + iVar5 * 4) * _DAT_005d85ec + _DAT_005d85ec;
  fVar6 = fVar11;
  if (_DAT_005d8568 < *(float *)(param_1 + 0xd4 + iVar5 * 4)) {
    lVar1 = (longlong)
            ROUND((_DAT_005d85bc - *(float *)(param_1 + 0xd4 + iVar5 * 4)) * _DAT_005dbe60 +
                  _DAT_005dbe5c);
    local_30[0]._0_4_ = (int)lVar1;
    if ((int)local_30[0] < 0) {
      local_30[0]._0_4_ = 0;
    }
    else if (0xff < (int)local_30[0]) {
      local_30[0]._0_4_ = 0xff;
    }
    fVar6 = (float)((((uint)fVar11 >> 8 & 0xffff0000) * (int)local_30[0] ^ (uint)fVar11) & 0xffffff
                   ^ ((uint)fVar11 >> 8 & 0xff0000) * (int)local_30[0]);
    local_30[0] = lVar1;
  }
  if ((*(float *)(param_1 + 0xf4 + iVar5 * 4) != _DAT_005d856c) ||
     (*(int *)(*(int *)(param_1 + 0x50) + 0x2fc) != 0)) {
    *(float *)(param_1 + 0xf4 + iVar5 * 4) =
         DAT_008a9e20 * _DAT_005d858c + *(float *)(param_1 + 0xf4 + iVar5 * 4);
  }
  pfVar4 = (float *)(param_1 + 0xf4 + *(int *)(param_1 + 0x58) * 4);
  if (_DAT_005d85e0 < *(float *)(param_1 + 0xf4 + *(int *)(param_1 + 0x58) * 4)) {
    if (*(int *)(*(int *)(param_1 + 0x50) + 0x2fc) == 0) {
      *pfVar4 = 0.0;
    }
    else {
      *pfVar4 = *pfVar4 - _DAT_005d85e0;
    }
  }
  if (*(int *)(*(int *)(param_1 + 0x50) + 0x2fc) != 0) {
    fVar12 = (float10)*(float *)(param_1 + 0xf4 + *(int *)(param_1 + 0x58) * 4);
    fVar12 = (float10)fsin(fVar12 + fVar12);
    fVar12 = fVar12 * (float10)_DAT_005d85ec + (float10)_DAT_005d85ec;
    fVar13 = (float10)_DAT_005d8568 - fVar12;
    local_30[0]._0_4_ =
         (int)(longlong)ROUND(fVar12 * (float10)_DAT_005d8c70 + fVar13 * (float10)_DAT_005db484);
    iVar5 = (int)local_30[0];
    local_30[0]._0_4_ =
         (int)(longlong)ROUND(fVar12 * (float10)_DAT_005db5e8 + fVar13 * (float10)_DAT_005db5e8);
    iVar10 = (int)local_30[0] * 0x100;
    local_30[0]._0_4_ =
         (int)(longlong)ROUND(fVar12 * (float10)_DAT_005dbe58 + fVar13 * (float10)_DAT_005db5e8);
    iVar5 = (iVar5 + iVar10) * 0x100 + (int)local_30[0];
    local_30[0] = (longlong)ROUND(fVar12 * (float10)_DAT_005dbc4c + fVar13 * (float10)_DAT_005d8c70)
    ;
    fVar6 = (float)(iVar5 * 0x100 + (int)local_30[0]);
  }
  iVar5 = *(int *)(param_1 + 0x58);
  fVar15 = _DAT_005d856c;
  if (*(float *)(param_1 + 0xd4 + iVar5 * 4) < _DAT_005d8568) {
    fVar15 = (_DAT_005d8568 - *(float *)(param_1 + 0xd4 + iVar5 * 4)) * _DAT_005d85ec;
  }
  CVBufTexture__DrawSpriteEx
            (local_10,local_c,0.011,*(void **)(param_1 + 0x16c),4,0,1.0,
             fVar15 + *(float *)(param_1 + 0xf4 + iVar5 * 4),fVar6,fVar16,DAT_00888a40 * fVar16,0.0,
             1.0,0.0,1.0);
  fVar16 = *(float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4);
  lVar1 = (longlong)
          ROUND(((_DAT_005d8568 - *(float *)(param_1 + 0xe4 + *(int *)(param_1 + 0x58) * 4)) +
                _DAT_005d8568) * _DAT_005dbe54);
  local_30[0]._0_4_ = (int)lVar1;
  if ((int)local_30[0] < 0) {
    local_30[0]._0_4_ = 0;
  }
  else if (0xff < (int)local_30[0]) {
    local_30[0]._0_4_ = 0xff;
  }
  fVar6 = (float)((((uint)fVar11 >> 8 & 0xffff0000) * (int)local_30[0] ^ (uint)fVar11) & 0xffffff ^
                 ((uint)fVar11 >> 8 & 0xff0000) * (int)local_30[0]);
  local_30[0] = lVar1;
  CVBufTexture__DrawSpriteEx
            (local_10,local_c,0.011,*(void **)(param_1 + 0x170),4,0,1.0,0.0,fVar6,fVar16,
             DAT_00888a40 * fVar16,0.0,1.0,0.0,1.0);
  CVBufTexture__DrawSpriteEx
            (local_10,local_c,0.011,*(void **)(param_1 + 0x174),4,0,1.0,0.0,fVar6,fVar16,
             DAT_00888a40 * fVar16,0.0,1.0,0.0,1.0);
  pfVar4 = (float *)(param_1 + 400 + *(int *)(param_1 + 0x58) * 4);
  *pfVar4 = DAT_008a9e20 * _DAT_005d8c40 + *pfVar4;
  pfVar4 = (float *)(param_1 + 400 + *(int *)(param_1 + 0x58) * 4);
  if (_DAT_005d8be8 <= *(float *)(param_1 + 400 + *(int *)(param_1 + 0x58) * 4)) {
    *pfVar4 = *pfVar4 - _DAT_005d8be8;
  }
  if ((*(int *)(DAT_008a9d84 + 8) != 0) &&
     (this = *(void **)(*(int *)(DAT_008a9d84 + 8) + 0x30), this != (void *)0x0)) {
    if ((*(byte *)((int)this + 0x34) & 0x10) == 0) {
      pfVar4 = (float *)(*(code *)**(undefined4 **)((int)this + 8))(local_30);
      local_20 = *pfVar4;
      local_1c = pfVar4[1];
      local_18 = pfVar4[2];
      local_14 = pfVar4[3];
    }
    else {
      CExplosionInitThing__Helper_004fd500(this,&local_20,unaff_EDI);
    }
    iVar5 = *(int *)(param_1 + 0x50);
    fVar12 = (float10)fpatan((float10)local_20 - (float10)*(float *)(iVar5 + 0x1c),
                             (float10)local_1c - (float10)*(float *)(iVar5 + 0x20));
    fVar12 = -fVar12;
    fVar13 = (float10)*(float *)(iVar5 + 0x114);
    if (((float10)_DAT_005d85c8 <= fVar12) || (fVar13 <= (float10)_DAT_005d85e4)) {
      if (((float10)_DAT_005d85e4 < fVar12) && (fVar13 < (float10)_DAT_005d85c8)) {
        fVar13 = fVar13 + (float10)_DAT_005d85e0;
      }
    }
    else {
      fVar13 = fVar13 - (float10)_DAT_005d85e0;
    }
    if (ABS(fVar12 - fVar13) < (float10)_DAT_005d85e4) {
      CDXEngine__PushTransformState
                (&DAT_009c65c0,(int)&local_10,(int)&local_20,*(float **)(param_1 + 0x54));
      p15 = 1.0;
      p14 = 0.0;
      p13 = 1.0;
      p12 = 0.0;
      p10 = 1.0;
      fVar15 = -NAN;
      fVar11 = 0.0;
      fVar6 = 1.0;
      iVar10 = 0;
      iVar5 = 4;
      fVar16 = DAT_00888a40;
      dVar14 = CDXEngine__Helper_0055dfe7
                         ((double)*(float *)(param_1 + 400 + *(int *)(param_1 + 0x58) * 4));
      local_30[0] = (longlong)ROUND(dVar14);
      CVBufTexture__DrawSpriteEx
                (local_10,local_c,0.011,*(void **)(param_1 + 0x178 + (int)local_30[0] * 4),iVar5,
                 iVar10,fVar6,fVar11,fVar15,p10,fVar16,p12,p13,p14,p15);
    }
  }
  return;
}
