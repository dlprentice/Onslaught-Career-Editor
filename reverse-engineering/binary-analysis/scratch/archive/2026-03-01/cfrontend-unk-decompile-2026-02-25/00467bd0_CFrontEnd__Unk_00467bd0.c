/* address: 0x00467bd0 */
/* name: CFrontEnd__Unk_00467bd0 */
/* signature: void __stdcall CFrontEnd__Unk_00467bd0(void * param_1, float param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFrontEnd__Unk_00467bd0(void *param_1,float param_2,float param_3)

{
  void *pvVar1;
  float fVar2;
  int unaff_EDI;
  float10 fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float scale_x;
  short *psVar7;
  float transition;
  int *out_extent_xy;
  int fade_out;
  float local_20;
  float local_1c;
  int local_18;
  int local_10;
  int local_8 [2];

  fVar5 = param_3;
  local_1c = 0.0;
  if ((param_2 < _DAT_005d8568) && (param_3 != 0.0)) {
    if (param_2 < _DAT_005d85ec) {
      return;
    }
    fVar3 = (float10)fsin((float10)param_2 * (float10)_DAT_005d85e8);
    local_1c = (float)(fVar3 * (float10)_DAT_005dbb80);
  }
  fVar4 = (param_2 - _DAT_005d85f8) * _DAT_005db4b8;
  fVar2 = _DAT_005d856c;
  if ((_DAT_005d856c <= fVar4) && (fVar2 = fVar4, _DAT_005d8568 < fVar4)) {
    fVar2 = _DAT_005d8568;
  }
  local_18 = (int)(longlong)ROUND(fVar2 * _DAT_005d8c70);
  if (local_18 < 0) {
    local_18 = 0;
  }
  else if (0xff < local_18) {
    local_18 = 0xff;
  }
  CDXSurf__RenderSurface
            (0x43c30000,local_1c + _DAT_005dbb7c,0x3ea8f5c3,DAT_0089d8d8,
             (local_18 * 0x7f & 0xff00U) << 0x10,0x3f800000,0x3f800000,4,0,0x3f800000,0);
  local_10 = 0xff;
  param_3 = 1.25;
  local_20 = 0.0;
  if ((param_2 < _DAT_005d8568) && (fVar5 == 0.0)) {
    if (_DAT_005d8cb4 <= param_2) {
      if (_DAT_005d8bec <= param_2) {
        if (_DAT_005d85f8 <= param_2) {
          fVar2 = _DAT_005d856c;
          if ((_DAT_005d856c <= fVar4) && (fVar2 = fVar4, _DAT_005d8568 < fVar4)) {
            fVar2 = _DAT_005d8568;
          }
          param_3 = fVar2 * _DAT_005d858c + _DAT_005d8568;
        }
        else {
          param_3 = 1.0;
        }
      }
      else {
        fVar4 = (param_2 - _DAT_005d8cb4) * _DAT_005dbb78;
        param_3 = _DAT_005d856c;
        if ((_DAT_005d856c <= fVar4) && (param_3 = fVar4, _DAT_005d8568 < fVar4)) {
          param_3 = _DAT_005d8568;
        }
        local_10 = (int)(longlong)ROUND(param_3 * _DAT_005d8c70);
        if (local_10 < 0) {
          local_10 = 0;
        }
        else if (0xff < local_10) {
          local_10 = 0xff;
        }
        local_20 = -((_DAT_005d8568 - param_3) * _DAT_005d8cb4);
      }
    }
    else {
      local_10 = 0;
    }
  }
  fVar3 = (float10)fsin((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  CDXSurf__RenderSurface
            ((float)(fVar3 * (float10)_DAT_005d8be8 + (float10)_DAT_005db4d8),
             (float)(fVar3 * (float10)_DAT_005d8be8 + (float10)local_1c + (float10)_DAT_005dbb74),
             0x3eb33333,DAT_0089d8cc,(local_10 * 0x3f & 0xff00U) << 0x10,param_3 * _DAT_005db4ac,
             param_3 * _DAT_005db4ac,4,0,0x3f800000,local_20);
  fVar4 = local_1c + _DAT_005dbb70;
  CDXSurf__RenderSurface
            (0x43c30000,fVar4,0x3e99999a,DAT_0089d8cc,
             ~(local_10 * 0xff0000) & 0xffffffU ^ local_10 * 0xff0000,param_3,param_3,4,0,0x3f800000
             ,local_20);
  local_18 = 0xff;
  local_20 = 0.0;
  if (((_DAT_005d8568 <= param_2) || (fVar5 != 0.0)) || (param_2 < _DAT_005d8cb4))
  goto LAB_004680c9;
  if (_DAT_005d8bec <= param_2) {
    if (_DAT_005d8bb0 <= param_2) {
      fVar6 = (param_2 - _DAT_005d8bb0) * _DAT_005dbb6c;
      fVar2 = _DAT_005d856c;
      if ((_DAT_005d856c <= fVar6) && (fVar2 = fVar6, _DAT_005d8568 < fVar6)) {
        fVar2 = _DAT_005d8568;
      }
      param_3 = _DAT_005d8568 - fVar2;
      local_18 = (int)(longlong)ROUND(param_3 * _DAT_005d8c70);
      if (-1 < local_18) goto joined_r0x00467ff7;
      local_18 = 0;
      goto LAB_00467ffe;
    }
    param_3 = 1.0;
  }
  else {
    fVar2 = (param_2 - _DAT_005d8cb4) * _DAT_005dbb78;
    param_3 = _DAT_005d856c;
    if ((_DAT_005d856c <= fVar2) && (param_3 = fVar2, _DAT_005d8568 < fVar2)) {
      param_3 = _DAT_005d8568;
    }
    local_18 = (int)(longlong)ROUND(param_3 * _DAT_005d8c70);
    if (local_18 < 0) {
      local_18 = 0;
    }
    else {
joined_r0x00467ff7:
      if (0xff < local_18) {
        local_18 = 0xff;
      }
    }
LAB_00467ffe:
    local_20 = -((_DAT_005d8568 - param_3) * _DAT_005d8cb4);
  }
  fVar3 = (float10)fsin((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  CDXSurf__RenderSurface
            ((float)(fVar3 * (float10)_DAT_005d8be8 + (float10)_DAT_005db4d8),
             (float)(fVar3 * (float10)_DAT_005d8be8 + (float10)local_1c + (float10)_DAT_005dbb74),
             0x3eb33333,DAT_0089d8d0,(local_18 * 0x3f & 0xff00U) << 0x10,param_3 * _DAT_005db4ac,
             param_3 * _DAT_005db4ac,4,0,0x3f800000,local_20);
  CDXSurf__RenderSurface
            (0x43c30000,fVar4,0x3e99999a,DAT_0089d8d0,
             ~(local_18 * 0xff0000) & 0xffffffU ^ local_18 * 0xff0000,param_3,param_3,4,0,0x3f800000
             ,local_20);
LAB_004680c9:
  fVar2 = -3.3961514e+38;
  if (fVar5 == 0.0) {
    fVar5 = (param_2 - _DAT_005d8bb0) * _DAT_005dbb6c;
    fVar2 = _DAT_005d856c;
    if ((_DAT_005d856c <= fVar5) && (fVar2 = fVar5, _DAT_005d8568 < fVar5)) {
      fVar2 = _DAT_005d8568;
    }
    local_18 = (int)(longlong)ROUND(fVar2 * _DAT_005d8c70);
    if (local_18 < 0) {
      local_18 = 0;
    }
    else if (0xff < local_18) {
      local_18 = 0xff;
    }
    fVar2 = (float)((local_18 * 0xff & 0xff00U) << 0x10 ^ 0x7f7f7f);
  }
  out_extent_xy = local_8;
  psVar7 = param_1;
  pvVar1 = CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__GetTextExtent(pvVar1,psVar7,out_extent_xy);
  fVar4 = fVar4 - _DAT_005d85bc;
  fade_out = 0;
  transition = 0.0;
  psVar7 = (short *)0x447a0000;
  scale_x = 1.0;
  fVar6 = 1.0;
  fVar5 = 0.1;
  pvVar1 = (void *)(_DAT_005dbb68 - (float)local_8[0] * _DAT_005d85ec);
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (pvVar1,fVar4,fVar5,fVar6,scale_x,fVar2,(int)param_1,psVar7,transition,fade_out,
             unaff_EDI);
  return;
}
