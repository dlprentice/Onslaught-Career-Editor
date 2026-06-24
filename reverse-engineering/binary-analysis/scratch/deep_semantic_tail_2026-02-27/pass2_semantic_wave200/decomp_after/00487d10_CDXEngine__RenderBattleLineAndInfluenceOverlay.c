/* address: 0x00487d10 */
/* name: CDXEngine__RenderBattleLineAndInfluenceOverlay */
/* signature: void __thiscall CDXEngine__RenderBattleLineAndInfluenceOverlay(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXEngine__RenderBattleLineAndInfluenceOverlay(void *this,void *param_1,void *param_2)

{
  float fVar1;
  int iVar2;
  int unaff_EDI;
  float local_4;

  CExplosionInitThing__SetupOverlayMarkerRenderState();
  *(float *)this = (float)*(int *)param_1;
  *(float *)((int)this + 4) = (float)*(int *)((int)param_1 + 4);
  *(float *)((int)this + 8) = (float)*(int *)((int)param_1 + 8);
  *(float *)((int)this + 0xc) = (float)*(int *)((int)param_1 + 0xc);
  iVar2 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
  if (iVar2 == 0) {
    local_4 = (_DAT_008aa4fc + _DAT_005d8bc0) - _DAT_0067a62c;
    fVar1 = local_4;
  }
  else {
    iVar2 = PLATFORM__GetWindowHeight();
    local_4 = (float)iVar2 * _DAT_005d85ec + _DAT_005dbebc;
    iVar2 = PLATFORM__GetWindowHeight();
    fVar1 = (float)iVar2 * _DAT_005d85ec + _DAT_005dbebc;
  }
  fVar1 = fVar1 - _DAT_005d8bc0;
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  CDXEngine__Helper_004b8850((int)DAT_008a9d84);
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  CVBufTexture__DrawSpriteEx
            ((_DAT_008aa4f8 - _DAT_005dbeb8) - _DAT_0067a628,local_4,0.001,
             *(void **)((int)this + 0x120),2,0,1.0,0.0,NAN,1.0,1.0,0.0,1.0,0.0,1.0);
  RenderState_Set(0x13,1);
  RenderState_Set(0x14,2);
  RenderState_Set(0x17,8);
  RenderState_Set(0xf,1);
  RenderState_Set(0xe,1);
  RenderState_Set(7,1);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  CVBufTexture__DrawSpriteEx
            (((_DAT_008aa4f8 - _DAT_005dbeb4) - _DAT_0067a628) + _DAT_005dbb64,fVar1 - _DAT_005dbb64
             ,0.005,*(void **)((int)this + 300),4,0,1.0,0.0,-NAN,1.5,1.5,-0.25,1.25,-0.25,1.25);
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  RenderState_Set(7,1);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  CDXEngine__Helper_004b82b0
            (DAT_008a9d84,(int)((_DAT_008aa4f8 - _DAT_005dbeb4) - _DAT_0067a628),fVar1,9.80909e-45,
             unaff_EDI);
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,2);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  CVBufTexture__DrawSpriteEx
            ((_DAT_008aa4f8 - _DAT_005dbeb8) - _DAT_0067a628,local_4,0.001,
             *(void **)((int)this + 0x11c),2,0,1.0,0.0,-3.1843154e+38,1.0,1.0,0.0,1.0,0.0,1.0);
  iVar2 = CInfluenceMapManager__IsEmpty();
  if (iVar2 == 0) {
    CExplosionInitThing__PopulateBattleLinePoints(*(int *)((int)this + 0x30));
    CDXBattleLine__Render();
  }
  else if (*(int *)((int)DAT_008a9d84 + 8) == 0) {
    CVBufTexture__DrawSpriteEx
              ((_DAT_008aa4f8 - _DAT_005dbeb0) - _DAT_0067a628,fVar1 - _DAT_005db2b8,0.001,
               *(void **)((int)this + 0x1d4),2,0,1.0,0.0,-NAN,1.0,1.0,0.0,1.0,0.0,1.0);
    return;
  }
  return;
}
