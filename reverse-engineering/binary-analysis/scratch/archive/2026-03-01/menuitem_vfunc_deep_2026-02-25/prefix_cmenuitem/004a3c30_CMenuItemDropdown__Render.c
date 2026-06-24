/* address: 0x004a3c30 */
/* name: CMenuItemDropdown__Render */
/* signature: undefined CMenuItemDropdown__Render(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMenuItemDropdown__Render(int *param_1,float param_2,float param_3)

{
  float p1;
  int iVar1;
  void *pvVar2;
  int iVar3;
  short *psVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  bool bVar8;
  float10 extraout_ST0;
  float10 fVar9;
  float fVar10;
  float fVar11;
  int *out_extent_xy;
  float p14;
  float p15;
  float fStack_f8;
  float fStack_f0;
  int iStack_e8;
  int iStack_e4;
  longlong lStack_e0;
  float fStack_d8;
  float fStack_d4;
  float fStack_d0;
  float fStack_cc;
  short asStack_c8 [100];

  iVar1 = (**(code **)(*param_1 + 0x3c))();
  if (iVar1 != param_1[7]) {
    param_1[7] = iVar1;
    param_1[8] = iVar1;
  }
  pvVar2 = (void *)(**(code **)(*param_1 + 8))();
  CTexture__Unk_0055e64e(asStack_c8,pvVar2);
  if (param_1[7] != param_1[8]) {
    PLATFORM__GetSysTimeFloat();
    CDXTexture__Unk_0055e3ea();
    fVar9 = (float10)fcos(extraout_ST0 * (float10)_DAT_005d85e0);
    lStack_e0 = (longlong)
                ROUND((fVar9 + (float10)_DAT_005d8568) * (float10)_DAT_005d85ec *
                      (float10)_DAT_005d8c70);
  }
  piVar7 = &iStack_e8;
  psVar4 = asStack_c8;
  pvVar2 = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(pvVar2,psVar4,piVar7);
  p1 = (float)iStack_e8 + (param_2 - (float)iStack_e8) + _DAT_005d8ba0;
  CPlatform__Font(&DAT_0088a0a8,1);
  CUnitAI__Unk_004659a0();
  if ((char)param_1[9] == '\0') {
    (**(code **)(*param_1 + 0x44))(param_1[8],0,0,0x3f800000,0x3f800000);
    CPlatform__Font(&DAT_0088a0a8,1);
    CUnitAI__Unk_004659a0();
  }
  else {
    iVar1 = 0;
    piVar7 = (int *)0x0;
    iVar3 = (**(code **)(*param_1 + 0x40))();
    if (0 < iVar3) {
      do {
        out_extent_xy = piVar7;
        psVar4 = (short *)(**(code **)(*param_1 + 0x44))(piVar7,&lStack_e0);
        pvVar2 = CPlatform__Font(&DAT_0088a0a8,1);
        CDXFont__GetTextExtent(pvVar2,psVar4,out_extent_xy);
        if (iVar1 < iStack_e4) {
          iVar1 = iStack_e4;
        }
        piVar7 = (int *)((int)piVar7 + 1);
        iVar3 = (**(code **)(*param_1 + 0x40))();
      } while ((int)piVar7 < iVar3);
    }
    iVar3 = (**(code **)(*param_1 + 0x40))();
    lStack_e0 = (longlong)ROUND(param_3 - (float)(((iVar3 + -1) * iStack_e4) / 2));
    iVar3 = (int)lStack_e0;
    if (DAT_0082b490 == (void *)0x0) {
      CPauseMenu__Unk_004d04d0();
    }
    fStack_f8 = (float)iVar3;
    fStack_f0 = 1.0;
    iVar3 = (**(code **)(*param_1 + 0x40))();
    lStack_e0 = CONCAT44(lStack_e0._4_4_,iVar3);
    fVar10 = (float)(iVar3 * iStack_e4);
    if (fStack_f8 < _DAT_005d856c) {
      fStack_f8 = 0.0;
    }
    if (_DAT_005db34c < fVar10 + fStack_f8) {
      if (fVar10 <= _DAT_005db34c) {
        fStack_f8 = _DAT_005db34c - fVar10;
      }
      else {
        fStack_f0 = _DAT_005db34c / fVar10;
        fStack_f8 = 0.0;
      }
    }
    p15 = 1.0;
    bVar8 = DAT_0089d950 != 0x11;
    p14 = 0.0;
    fVar11 = 1.0;
    fVar10 = 0.0;
    iVar5 = (**(code **)(*param_1 + 0x40))();
    CVBufTexture__DrawSpriteEx
              (p1,fStack_f8,0.004,DAT_0082b490,0,0,1.0,0.0,
               (float)((-(uint)bVar8 & 0x1806d7) - 0xd7c697),(float)(iVar1 + 3) * _DAT_005dbb50,
               (float)(iVar5 * iStack_e4) * fStack_f0 * _DAT_005dbb50,fVar10,fVar11,p14,p15);
    iVar1 = 0;
    fStack_d0 = (float)iStack_e4 * fStack_f0;
    if (0 < iVar3) {
      fStack_d4 = p1 + _DAT_005d8ba0;
      do {
        fStack_d8 = (float)iStack_e8 + p1 + _DAT_005d8ba0;
        fVar10 = fStack_d0 + fStack_f8;
        uVar6 = CUnitAI__Unk_004693d0((int)fStack_d4,(int)fStack_f8,(int)fStack_d8,(int)fVar10);
        if ((char)uVar6 != '\0') {
          param_1[8] = iVar1;
        }
        (**(code **)(*param_1 + 0x44))(iVar1,0,0,0x3f800000,fStack_f0);
        fVar11 = fStack_d4;
        CPlatform__Font(&DAT_0088a0a8,1);
        CUnitAI__Unk_004659a0();
        fStack_d8 = (float)iStack_e4 + fStack_f8;
        fStack_cc = (float)iStack_e8 + p1 + _DAT_005d8ba0;
        uVar6 = CMonitor__Unk_00469400((int)fVar11,(int)fStack_f8,(int)fStack_cc,(int)fStack_d8);
        if ((char)uVar6 != '\0') {
          param_1[8] = iVar1;
          *(undefined1 *)(param_1 + 9) = 0;
          if ((*(char *)((int)param_1 + 0x25) == '\0') && (param_1[7] != iVar1)) {
            param_1[7] = iVar1;
            (**(code **)(*param_1 + 0x38))(iVar1);
          }
          CFrontEnd__PlaySound(1);
        }
        iVar1 = iVar1 + 1;
        fStack_f8 = fVar10;
      } while (iVar1 < (int)lStack_e0);
    }
    iVar1 = CUnitAI__Unk_0044dea0(0x675688);
    if ((iVar1 == 0) && (DAT_0089be28 != 0)) {
      *(undefined1 *)(param_1 + 9) = 0;
      param_1[8] = param_1[7];
      DAT_0089be28 = 0;
      CFrontEnd__PlaySound(2);
      return;
    }
  }
  return;
}
