/* address: 0x004a37c0 */
/* name: CMenuItem__RenderValueBar */
/* signature: void __thiscall CMenuItem__RenderValueBar(void * this, float x, float y, int interactive) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMenuItem__RenderValueBar(void *this,float x,float y,int interactive)

{
  float fVar1;
  float fVar2;
  short *text;
  void *this_00;
  float p9;
  int iVar3;
  uint uVar4;
  float10 extraout_ST0;
  float10 fVar5;
  int *out_extent_xy;
  int iStack_14;
  int aiStack_10 [2];
  longlong lStack_8;

  text = (short *)(**(code **)(*(int *)this + 8))();
  if (interactive == 0) {
    *(undefined4 *)((int)this + 0x24) = *(undefined4 *)((int)this + 0x28);
    (**(code **)(*(int *)this + 0x38))();
  }
  if (*(int *)((int)this + 0x1c) == 0) {
    (**(code **)(*(int *)this + 0x34))();
  }
  out_extent_xy = aiStack_10;
  this_00 = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(this_00,text,out_extent_xy);
  fVar1 = (float)aiStack_10[0] + ((x - (float)(aiStack_10[0] / 2)) - _DAT_005dc570) + _DAT_005d8ba0;
  CPlatform__Font(&DAT_0088a0a8,1);
  CUnitAI__Unk_004659a0();
  RenderState_Set(0x1b,1);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  fVar2 = y + _DAT_005d8c44;
  CVBufTexture__DrawSpriteEx
            (fVar1 + _DAT_005d85d8,fVar2,0.003,*(void **)((int)this + 0x1c),4,0,1.0,3.1415927,-NAN,
             0.3,0.3,0.0,1.0,0.0,1.0);
  CVBufTexture__DrawSpriteEx
            (fVar1 + _DAT_005dc56c,fVar2,0.003,*(void **)((int)this + 0x1c),4,0,1.0,0.0,-NAN,0.3,0.3
             ,0.0,1.0,0.0,1.0);
  iStack_14 = 0;
  if (0 < *(int *)((int)this + 0x2c)) {
    do {
      p9 = -2.7689643e+38;
      if (iStack_14 < *(int *)((int)this + 0x24)) {
        if (*(int *)((int)this + 0x28) <= iStack_14) {
          if (*(int *)((int)this + 0x24) <= iStack_14) goto LAB_004a396b;
          goto LAB_004a3974;
        }
        p9 = -1.7097195e+38;
      }
      else {
LAB_004a396b:
        if (iStack_14 < *(int *)((int)this + 0x28)) {
LAB_004a3974:
          PLATFORM__GetSysTimeFloat();
          CDXTexture__Unk_0055e3ea();
          fVar5 = (float10)fsin(extraout_ST0 * (float10)_DAT_005d85e8);
          fVar5 = (fVar5 + (float10)_DAT_005d8568) * (float10)_DAT_005d85ec;
          lStack_8._0_4_ =
               (int)(longlong)
                    ROUND(fVar5 * (float10)_DAT_005d8c70 +
                          ((float10)_DAT_005d8568 - fVar5) * (float10)_DAT_005d8c70);
          iVar3 = (int)lStack_8 * 0x10000;
          lStack_8._0_4_ =
               (int)(longlong)
                    ROUND(fVar5 * (float10)_DAT_005d9640 +
                          ((float10)_DAT_005d8568 - fVar5) * (float10)_DAT_005dc568);
          iVar3 = iVar3 + (int)lStack_8;
          lStack_8 = (longlong)ROUND(fVar5 * (float10)_DAT_005dc564);
          p9 = (float)(iVar3 * 0x100 + (int)lStack_8 * -0x10001);
        }
      }
      CVBufTexture__DrawSpriteEx
                (((float)iStack_14 * _DAT_005d9640) / (float)*(int *)((int)this + 0x2c) + fVar1 +
                 _DAT_005dbe80,fVar2,0.003,*(void **)((int)this + 0x20),8,0,1.0,0.0,p9,
                 (_DAT_005d9640 / (float)*(int *)((int)this + 0x2c) - _DAT_005d8568) * _DAT_005dbb50
                 ,0.7,0.0,1.0,0.0,1.0);
      iStack_14 = iStack_14 + 1;
    } while (iStack_14 < *(int *)((int)this + 0x2c));
  }
  if (interactive != 0) {
    fVar2 = y + _DAT_005d8bc0;
    uVar4 = CMonitor__Unk_00469400((int)fVar1,(int)y,(int)(fVar1 + _DAT_005d8610),(int)fVar2);
    if ((char)uVar4 != '\0') {
      (**(code **)(*(int *)this + 4))(0,0x36,0x3f800000);
      return;
    }
    uVar4 = CMonitor__Unk_00469400
                      ((int)(fVar1 + _DAT_005db538),(int)y,(int)(fVar1 + _DAT_005db4d0),(int)fVar2);
    if ((char)uVar4 != '\0') {
      (**(code **)(*(int *)this + 4))(0,0x37,0x3f800000);
    }
  }
  return;
}
