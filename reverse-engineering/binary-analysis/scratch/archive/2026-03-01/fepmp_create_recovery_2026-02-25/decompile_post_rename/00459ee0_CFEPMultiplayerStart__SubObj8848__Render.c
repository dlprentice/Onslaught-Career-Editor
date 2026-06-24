/* address: 0x00459ee0 */
/* name: CFEPMultiplayerStart__SubObj8848__Render */
/* signature: undefined CFEPMultiplayerStart__SubObj8848__Render(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFEPMultiplayerStart__SubObj8848__Render(int *param_1,float param_2,float param_3)

{
  int iVar1;
  uint uVar2;
  int extraout_EAX;
  int extraout_EAX_00;
  short *color;
  void *pvVar3;
  short *psVar4;
  float fVar5;
  uint uVar6;
  int unaff_EDI;
  float fVar7;
  void *this;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float transition;
  int iVar12;
  int *out_extent_xy;
  float fStack_60;
  float *pfStack_5c;
  float fStack_54;
  float fStack_50;
  int iStack_48;
  int *piStack_44;
  int iStack_40;
  int iStack_38;
  int iStack_30;
  float *pfStack_2c;
  int iStack_20;
  int iStack_10;
  int aiStack_8 [2];

  if ((param_3 == 7.00649e-45) || (param_3 == 8.40779e-45)) {
    fStack_50 = 1.0;
  }
  else {
    fStack_50 = (param_2 - _DAT_005d8bc4) * _DAT_005d85bc;
    if (_DAT_005d856c <= fStack_50) {
      if (_DAT_005d8568 < fStack_50) {
        fStack_50 = _DAT_005d8568;
      }
    }
    else {
      fStack_50 = _DAT_005d856c;
    }
  }
  CUnitAI__Unk_00452fd0(fStack_50);
  CFrontEnd__EnableAdditiveAlpha();
  iVar1 = param_1[0xd17];
  if (0 < iVar1) {
    do {
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
  }
  CFrontEnd__EnableModulateAlpha();
  fStack_60 = _DAT_005db53c - (float)param_1[0xd18];
  fStack_50 = (param_2 - _DAT_005d8bc4) * _DAT_005d85bc;
  fVar7 = _DAT_005d856c;
  if ((_DAT_005d856c <= fStack_50) && (fVar7 = fStack_50, _DAT_005d8568 < fStack_50)) {
    fVar7 = _DAT_005d8568;
  }
  iStack_48 = 0;
  iStack_10 = (int)(longlong)ROUND(fVar7 * _DAT_005d8c70);
  iVar1 = iStack_10;
  if (0 < param_1[0xd17]) {
    pfStack_2c = (float *)(param_1 + 0x15f);
    iStack_30 = 0;
    piStack_44 = param_1;
    do {
      piStack_44 = piStack_44 + 1;
      iStack_40 = 0;
      fStack_54 = (float)(*piStack_44 + -1) * _DAT_005db538 * _DAT_005d85ec + _DAT_005db520;
      if (0 < *piStack_44) {
        iStack_38 = 0;
        uVar2 = iVar1 * 0xff0000;
        pfStack_5c = pfStack_2c;
        do {
          RenderState_Set(0x13,1);
          RenderState_Set(0x14,2);
          D3DStateCache__SetState114Raw(0,1,3);
          D3DStateCache__SetState114Raw(0,2,3);
          CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
          CDXSurf__RenderSurface
                    (fStack_60,fStack_54,0x3e1eb852,DAT_0089d808,uVar2 | 0xffffff,0x3f800000,
                     0x3f800000,4,0,0x3f800000,0);
          RenderState_Set(0x13,5);
          RenderState_Set(0x14,6);
          D3DStateCache__SetState114Raw(0,1,1);
          D3DStateCache__SetState114Raw(0,2,1);
          CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
          fVar7 = _DAT_008a9570 * _DAT_005d8cb8 +
                  ((float)iStack_38 + (float)iStack_30) * _DAT_005db534;
          CDXSurf__RenderSurface
                    (fStack_60,fStack_54,0x3e23d70b,DAT_0089d814,uVar2 | 0xffffff,0x3f800000,
                     0x3f800000,4,4,fVar7,0);
          if (_DAT_005d856c < *pfStack_5c) {
            fVar5 = *pfStack_5c + *pfStack_5c;
            fVar8 = _DAT_005d856c;
            if ((_DAT_005d856c <= fVar5) && (fVar8 = fVar5, _DAT_005d8568 < fVar5)) {
              fVar8 = _DAT_005d8568;
            }
            iStack_10 = (int)(longlong)ROUND(fVar8 * _DAT_005d8c70);
            CDXSurf__RenderSurface
                      (fStack_60,fStack_54,0x3e23d70b,DAT_0089d818,
                       ((iStack_10 * iVar1) / 0xff) * 0xff0000 | 0xffffff,0x3f800000,0x3f800000,4,4,
                       fVar7,0);
          }
          DAT_009c68ac = 0;
          DAT_009c690d = 1;
          if ((((param_2 == _DAT_005d8568) || (param_1[0xd1a] != iStack_48)) ||
              (param_1[0xd1b] != iStack_40)) ||
             ((param_3 != 7.00649e-45 && (param_3 != 8.40779e-45)))) {
            if (0 < iVar1) {
              fVar7 = *pfStack_5c * _DAT_005d8de8;
              uVar6 = ~uVar2 & 0xffffff ^ uVar2;
              fVar5 = *pfStack_5c * _DAT_005d858c + _DAT_005d8568;
              CDXSurf__RenderSurface
                        (fStack_60,fStack_54,0x3e19999a,DAT_0089d804,uVar6,0x3f800000,0x3f800000,4,0
                         ,0x3f800000,fVar7);
              CDXSurf__RenderSurface
                        (fStack_60,fStack_54,0x3e19999a,DAT_0089d800,uVar6,fVar5,fVar5,4,0,
                         0x3f800000,-fVar7);
            }
          }
          else if (_DAT_005d856c < param_2) {
            fVar7 = _DAT_005d8568 - param_2;
            fVar9 = param_2 * _DAT_005db530;
            fVar8 = fVar7 * _DAT_005d8bd8 + _DAT_005d85c0;
            fVar5 = (_DAT_005db52c - fStack_60) * fVar7 + fStack_60;
            fVar7 = (_DAT_005d85f4 - fStack_54) * fVar7 + fStack_54;
            CDXSurf__RenderSurface
                      (fVar5,fVar7,0x3e19999a,DAT_0089d810,0xffffffff,fVar8,fVar8,4,0,0x3f800000,
                       -fVar9);
            CDXSurf__RenderSurface
                      (fVar5,fVar7,0x3e19999a,DAT_0089d80c,0xffffffff,fVar8 * _DAT_005db528,
                       fVar8 * _DAT_005db528,4,0,0x3f800000,fVar9);
          }
          iStack_20 = 0;
          if (0 < (int)pfStack_5c[300]) {
            do {
              if (0 < iVar1) {
                CFrontEnd__DrawLine();
              }
              iStack_20 = iStack_20 + 1;
            } while (iStack_20 < (int)pfStack_5c[300]);
          }
          fStack_54 = fStack_54 - _DAT_005db538;
          pfStack_5c = pfStack_5c + 1;
          iStack_40 = iStack_40 + 1;
          iStack_38 = iStack_38 + 7;
        } while (iStack_40 < *piStack_44);
      }
      fStack_60 = fStack_60 + _DAT_005db020;
      iStack_30 = iStack_30 + 0xb;
      pfStack_2c = pfStack_2c + 6;
      iStack_48 = iStack_48 + 1;
    } while (iStack_48 < param_1[0xd17]);
  }
  if ((param_3 == 7.00649e-45) || (param_3 == 8.40779e-45)) {
    fStack_50 = 1.0;
  }
  else if (_DAT_005d856c <= fStack_50) {
    if (_DAT_005d8568 < fStack_50) {
      fStack_50 = _DAT_005d8568;
    }
  }
  else {
    fStack_50 = _DAT_005d856c;
  }
  CFrontEnd__RenderOverlayEffects(fStack_50);
  iStack_10 = (int)(longlong)ROUND((param_2 * _DAT_005d85bc - _DAT_005d8ba0) * _DAT_005d8c70);
  if (iStack_10 < 0) {
    iStack_10 = 0;
  }
  else if (0xff < iStack_10) {
    iStack_10 = 0xff;
  }
  fVar7 = (_DAT_005d8568 - param_2) - _DAT_005d858c;
  if (fVar7 < _DAT_005d856c) {
    fVar7 = _DAT_005d856c;
  }
  iVar12 = 0;
  pvVar3 = (void *)(_DAT_005db524 - fVar7 * fVar7 * _DAT_005db3fc);
  transition = 0.0;
  fVar5 = (float)(iStack_10 << 0x18 | 0x7f7f7f);
  fVar7 = PLATFORM__GetSysTimeFloat();
  psVar4 = (short *)(fVar7 - (float)param_1[0xd1d]);
  CUnitAI__Unk_00469550(param_1[param_1[0xd1b] + param_1[0xd1a] * 6 + 0x33]);
  fVar11 = 1.0;
  fVar10 = 0.7;
  fVar9 = 0.15;
  fVar8 = 160.0;
  this = pvVar3;
  fVar7 = fVar5;
  iVar1 = extraout_EAX;
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (this,fVar8,fVar9,fVar10,fVar11,fVar7,iVar1,psVar4,transition,iVar12,unaff_EDI);
  iVar12 = 0;
  fVar11 = 0.0;
  fVar7 = PLATFORM__GetSysTimeFloat();
  psVar4 = (short *)(fVar7 - (float)param_1[0xd1c]);
  CUnitAI__Unk_00469c20(param_1[param_1[0xd1b] + param_1[0xd1a] * 6 + 0x33] / 100);
  fVar10 = 1.0;
  fVar9 = 0.7;
  fVar8 = 0.15;
  fVar7 = 130.0;
  iVar1 = extraout_EAX_00;
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (pvVar3,fVar7,fVar8,fVar9,fVar10,fVar5,iVar1,psVar4,fVar11,iVar12,unaff_EDI);
  color = Text__AsciiToWideScratch(s_E3_2002_Build___Beta_work_in_pro_006292b8);
  out_extent_xy = aiStack_8;
  psVar4 = color;
  pvVar3 = CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__GetTextExtent(pvVar3,psVar4,out_extent_xy);
  iVar1 = 0;
  fVar11 = 0.0;
  fVar7 = PLATFORM__GetSysTimeFloat();
  psVar4 = (short *)(fVar7 - (float)param_1[0xd1e]);
  fVar7 = (float)(iStack_10 << 0x18 | 0x7f7f3f);
  fVar10 = 1.0;
  fVar9 = 1.0;
  fVar8 = 0.15;
  fVar5 = 350.0;
  pvVar3 = (void *)(_DAT_005db3e8 - (float)aiStack_8[0] * _DAT_005d85ec);
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (pvVar3,fVar5,fVar8,fVar9,fVar10,fVar7,(int)color,psVar4,fVar11,iVar1,unaff_EDI);
  CUnitAI__Unk_00453140(7.00649e-45,param_2);
  CUnitAI__Unk_00453140(1.4013e-45,param_2);
  psVar4 = CUnitAI__Unk_0046a2a0(10);
  CFrontEnd__DrawTitleBar(psVar4,param_2,param_3);
  return;
}
