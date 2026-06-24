/* address: 0x00521260 */
/* name: CFEPVirtualKeyboard__Helper_00521260 */
/* signature: void __thiscall CFEPVirtualKeyboard__Helper_00521260(void * this, int param_1, float param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFEPVirtualKeyboard__Helper_00521260(void *this,int param_1,float param_2,int param_3,void *param_4)

{
  uint uVar1;
  int iVar2;
  void *pvVar3;
  uint uVar4;
  uint uVar5;
  float fVar6;
  int unaff_EDI;
  short *psVar7;
  float10 extraout_ST0;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  int *piVar12;
  short *text;
  short *psVar13;
  float fVar14;
  int iVar15;
  int local_50 [2];
  int aiStack_48 [2];
  short asStack_40 [32];

  iVar2 = param_3;
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  CFrontEnd__DrawPanel();
  CFrontEnd__DrawBox();
  piVar12 = local_50;
  psVar13 = (short *)((int)this + 4);
  psVar7 = psVar13;
  pvVar3 = CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__GetTextExtent(pvVar3,psVar7,piVar12);
  param_3 = (int)(((DAT_0063fd20 - DAT_0063fd1c) * _DAT_005d85ec + DAT_0063fd1c) -
                 (float)(local_50[0] >> 1));
  if (*(char *)((int)this + 0x48) != '\0') {
    CFrontEnd__DrawPanel();
  }
  iVar15 = 0;
  fVar14 = 0.0;
  text = (short *)0x447a0000;
  fVar6 = (float)(iVar2 * 0xff0000 | 0xffffff);
  fVar11 = 1.0;
  fVar10 = 1.0;
  fVar9 = 0.13;
  pvVar3 = (void *)param_3;
  fVar8 = (float)param_1;
  psVar7 = psVar13;
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__DrawTextDynamic
            (pvVar3,fVar8,fVar9,fVar10,fVar11,fVar6,(int)psVar7,text,fVar14,iVar15,unaff_EDI);
  if (*(char *)((int)this + 0x48) == '\0') {
    PLATFORM__GetSysTimeFloat();
    CPDSimpleSprite__Helper_0055e3ea();
    if (extraout_ST0 < (float10)_DAT_005e4a30) {
      uVar1 = *(uint *)((int)this + 0x44);
      param_1 = 0x49;
      uVar4 = 0;
      if (0 < (int)uVar1) {
        psVar7 = asStack_40;
        for (uVar4 = uVar1 >> 1; uVar4 != 0; uVar4 = uVar4 - 1) {
          *(undefined4 *)psVar7 = *(undefined4 *)psVar13;
          psVar13 = psVar13 + 2;
          psVar7 = psVar7 + 2;
        }
        for (uVar5 = (uint)((uVar1 & 1) != 0); uVar4 = uVar1, uVar5 != 0; uVar5 = uVar5 - 1) {
          *psVar7 = *psVar13;
          psVar13 = psVar13 + 1;
          psVar7 = psVar7 + 1;
        }
      }
      asStack_40[uVar4] = 0;
      piVar12 = aiStack_48;
      psVar13 = asStack_40;
      pvVar3 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar3,psVar13,piVar12);
      iVar15 = 0;
      fVar14 = 0.0;
      piVar12 = &param_1;
      psVar13 = (short *)0x447a0000;
      fVar6 = (float)(iVar2 * 0xff0000 & 0xff0080a0U | 0x80a0);
      pvVar3 = (void *)((float)aiStack_48[0] + (float)param_3 + _DAT_005d8568);
      fVar11 = 1.0;
      fVar10 = 1.0;
      fVar9 = 0.13;
      fVar8 = DAT_0063fd30;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawTextDynamic
                (pvVar3,fVar8,fVar9,fVar10,fVar11,fVar6,(int)piVar12,psVar13,fVar14,iVar15,unaff_EDI
                );
    }
  }
  return;
}
