/* address: 0x004879e0 */
/* name: CExplosionInitThing__Unk_004879e0 */
/* signature: void __thiscall CExplosionInitThing__Unk_004879e0(void * this, void * param_1, int param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CExplosionInitThing__Unk_004879e0(void *this,void *param_1,int param_2,float param_3)

{
  int iVar1;
  float fVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;
  int iVar8;
  int unaff_EBP;
  int unaff_ESI;
  int unaff_EDI;
  float fVar9;

  iVar3 = *(int *)((int)param_1 + 0x1c);
  if ((iVar3 != 0) && ((*(byte *)(iVar3 + 0x2c) & 4) == 0)) {
    CEngine__Unk_0044a0d0(&DAT_0089c9a0,param_2,unaff_EDI);
    iVar1 = param_2 * 3 + 0x87;
    *(float *)this = (float)*(int *)(&DAT_0089c9a0 + iVar1 * 8);
    *(float *)((int)this + 4) = (float)(int)(&DAT_0089c9a4)[iVar1 * 2];
    *(float *)((int)this + 8) = (float)(int)(&DAT_0089c9a8)[iVar1 * 2];
    iVar7 = (&DAT_0089c9ac)[iVar1 * 2];
    *(undefined4 *)((int)this + 0x18) = *(undefined4 *)this;
    *(undefined4 *)((int)this + 0x20) = *(undefined4 *)((int)this + 8);
    *(float *)((int)this + 0xc) = (float)iVar7;
    *(undefined4 *)((int)this + 0x1c) = *(undefined4 *)this;
    *(undefined4 *)((int)this + 0x24) = *(undefined4 *)((int)this + 0xc);
    iVar7 = PLATFORM__GetWindowWidth();
    iVar8 = PLATFORM__GetWindowHeight();
    fVar5 = _DAT_0062ce74 * (float)iVar7;
    fVar9 = _DAT_0062ce74 * (float)iVar8;
    fVar4 = ((float)iVar7 - fVar5) * _DAT_005d85ec;
    fVar6 = ((float)iVar8 - fVar9) * _DAT_005d85ec;
    if (*(float *)((int)this + 0x20) < fVar4) {
      fVar2 = *(float *)((int)this + 0x20);
      *(float *)((int)this + 0x20) = fVar4;
      *(float *)((int)this + 0x18) = *(float *)((int)this + 0x18) - (fVar4 - fVar2);
    }
    if (*(float *)((int)this + 0x24) < fVar6) {
      fVar2 = *(float *)((int)this + 0x24);
      *(float *)((int)this + 0x24) = fVar4;
      *(float *)((int)this + 0x1c) = *(float *)((int)this + 0x1c) - (fVar6 - fVar2);
    }
    fVar4 = fVar4 + fVar5;
    if (fVar4 < *(float *)((int)this + 0x18) + *(float *)((int)this + 0x20)) {
      *(float *)((int)this + 0x18) = fVar4 - *(float *)((int)this + 0x20);
    }
    if (fVar6 + fVar9 < *(float *)((int)this + 0x24) + *(float *)((int)this + 0x1c)) {
      *(float *)((int)this + 0x1c) = (fVar6 + fVar9) - *(float *)((int)this + 0x24);
    }
    *(int *)((int)this + 0x50) = iVar3;
    *(undefined **)((int)this + 0x54) = &DAT_0089c9a0 + iVar1 * 8;
    *(int *)((int)this + 0x58) = param_2;
    *(float *)((int)this + 0x14) = *(float *)((int)this + 0xc) + *(float *)((int)this + 4);
    *(float *)((int)this + 0x10) = *(float *)((int)this + 8) + *(float *)this;
    *(float *)((int)this + 0x2c) = *(float *)((int)this + 0x24) + *(float *)((int)this + 0x1c);
    *(float *)((int)this + 0x28) = *(float *)((int)this + 0x18) + *(float *)((int)this + 0x20);
    CUnitAI__Unk_00482090();
    RenderState_Set(0xf,0);
    CUnitAI__Unk_00486e00((int)this);
    CSphere__Unk_00482590((int)this);
    if (DAT_008a9d90 != 0) {
      CUnitAI__Unk_0047fb50(unaff_ESI,unaff_EBP,(int)fVar9);
    }
    CUnitAI__Unk_00483530((int)this);
    CUnitAI__Unk_00484340((int)this);
    CUnitAI__Unk_004858d0((int)this);
    CUnitAI__Unk_00485d50((int)this);
    CUnitAI__Unk_00486940((int)this);
    CUnitAI__Unk_00484c50((int)this);
  }
  return;
}
