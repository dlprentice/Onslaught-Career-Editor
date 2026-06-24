/* address: 0x004b8850 */
/* name: CDXEngine__RenderMessageBoxOverlay */
/* signature: void __fastcall CDXEngine__RenderMessageBoxOverlay(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXEngine__RenderMessageBoxOverlay(int param_1)

{
  bool bVar1;
  float fVar2;
  int iVar3;
  int unaff_EDI;
  int iVar4;
  undefined1 local_560 [1376];

  if (3 < DAT_008a9ac0) {
    CMessageBox__StopVoicePlaybackIfNotInCutscene(param_1);
    return;
  }
  iVar4 = 0;
  if (*(int *)(param_1 + 8) == 0) {
    if (*(float *)(param_1 + 0x2c4) <= _DAT_005d8568) {
      fVar2 = *(float *)(param_1 + 0x2c4) - DAT_008a9e20 * _DAT_005d8c40;
      *(float *)(param_1 + 0x2c4) = fVar2;
      if (fVar2 < _DAT_005d856c) {
        *(undefined4 *)(param_1 + 0x2c4) = 0;
      }
    }
    else if (*(int *)(param_1 + 0x18) == 0) {
      bVar1 = _DAT_005d8568 <= *(float *)(param_1 + 0x2c4);
      fVar2 = _DAT_005d95b4;
      if (!bVar1) {
        fVar2 = _DAT_005d8574;
      }
      fVar2 = ((*(float *)(param_1 + 0x2c4) - _DAT_005d8ba0) + fVar2) * DAT_008a9e20 * _DAT_005d85ec
              + *(float *)(param_1 + 0x2c4);
      *(float *)(param_1 + 0x2c4) = fVar2;
      if (bVar1) {
        if (fVar2 < _DAT_005d8568) {
          *(undefined4 *)(param_1 + 0x2c4) = 0x3f800000;
        }
      }
      else if (_DAT_005d8568 < fVar2) {
        *(undefined4 *)(param_1 + 0x2c4) = 0x3f800000;
      }
    }
    if (*(float *)(param_1 + 0x2c4) == _DAT_005d856c) {
      return;
    }
  }
  else if (_DAT_005d8568 <= *(float *)(param_1 + 0x2c4)) {
    fVar2 = (_DAT_005d8ba0 - *(float *)(param_1 + 0x2c4)) * DAT_008a9e20 * _DAT_005d85ec +
            *(float *)(param_1 + 0x2c4);
    *(float *)(param_1 + 0x2c4) = fVar2;
    if (ABS(_DAT_005d8ba0 - fVar2) < _DAT_005d8574) {
      *(undefined4 *)(param_1 + 0x2c4) = 0x40000000;
    }
  }
  else {
    fVar2 = DAT_008a9e20 * _DAT_005d8c40 + *(float *)(param_1 + 0x2c4);
    *(float *)(param_1 + 0x2c4) = fVar2;
    if (_DAT_005d8568 < fVar2) {
      *(undefined4 *)(param_1 + 0x2c4) = 0x3f800000;
    }
  }
  iVar3 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
  if (iVar3 != 0) {
    PLATFORM__GetWindowHeight();
  }
  CUnitAI__Helper_00482210();
  if ((*(void **)(param_1 + 8) != (void *)0x0) && (_DAT_005d8ba0 <= *(float *)(param_1 + 0x2c4))) {
    CMessage__WordWrapToLineBuffer
              (*(void **)(param_1 + 8),(int)local_560,DAT_0062ce5c,*(int *)(param_1 + 0x1bc),
               unaff_EDI);
    iVar3 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
    if (iVar3 != 0) {
      PLATFORM__GetWindowHeight();
    }
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CPlatform__Font(&DAT_0088a0a8,1);
    CDXEngine__DrawTextScaledWithShadow();
    do {
      DAT_009c68ad = 0;
      DAT_009c6910 = 1;
      DAT_009c68ac = 0;
      DAT_009c690d = 1;
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0);
      CPlatform__Font(&DAT_0088a0a8,1);
      CDXEngine__DrawTextScaledWithShadow();
      iVar4 = iVar4 + 0xf;
    } while (iVar4 < 0x4b);
  }
  return;
}
