/* address: 0x00550d50 */
/* name: CDXEngine__ApplyPendingRenderState */
/* signature: void __thiscall CDXEngine__ApplyPendingRenderState(void * this, char force_raw) */


/* WARNING: Removing unreachable block (ram,0x005511c4) */
/* WARNING: Removing unreachable block (ram,0x005511cd) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__ApplyPendingRenderState(void *this,char force_raw)

{
  uint uVar1;
  int iVar2;
  int extraout_EAX;
  int *piVar3;
  char *unaff_ESI;
  undefined4 *puVar4;
  undefined4 *puVar5;
  bool bVar6;
  bool bVar7;
  bool bVar8;
  undefined4 auStack_40 [14];
  float fStack_8;

  if (*(char *)((int)this + 0x34d) != '\0') {
    if (DAT_0089d680 != '\0') {
      *(undefined1 *)((int)this + 0x2ec) = 0;
    }
    RenderState_Set(0x1c,(uint)*(byte *)((int)this + 0x2ec));
    *(undefined1 *)((int)this + 0x34d) = 0;
  }
  if (*(char *)((int)this + 0x350) != '\0') {
    RenderState_Set(0x89,(uint)*(byte *)((int)this + 0x2ed));
    *(undefined1 *)((int)this + 0x350) = 0;
  }
  if (*(int *)((int)this + 0xe54) != 0) {
    RenderState_Set_23_8C_Compat('\x01');
  }
  if (*(int *)((int)this + 0xe54) != 0) {
    CVertexShader__Unk_00502290(*(int *)((int)this + 0xe54));
    *(undefined4 *)((int)this + 0xe54) = 0;
  }
  if (*(int *)((int)this + 0xe58) != 0) {
    if (DAT_00854e6c != '\0') {
      CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\x01');
    }
    D3DStateCache__SetStateCached(0,0xb,0);
    D3DStateCache__SetStateCached(1,0xb,1);
    D3DStateCache__SetStateCached(2,0xb,2);
    D3DStateCache__SetStateCached(3,0xb,3);
    D3DStateCache__SetStateCached(0,0x18,0);
    D3DStateCache__SetStateCached(1,0x18,0);
    D3DStateCache__SetStateCached(2,0x18,0);
    D3DStateCache__SetStateCached(3,0x18,0);
    CEngine__SetShaderObject(&DAT_00855bb0,*(void **)((int)this + 0xe58));
    return;
  }
  if ((force_raw != '\0') && (DAT_0063c108 != '\0')) {
    *(undefined4 *)((int)this + 0xe54) = 0;
    bVar6 = *(int *)((int)this + 0xe30) != 0;
    bVar7 = *(char *)((int)this + 0x2f5) != '\0';
    force_raw = bVar7 || bVar6;
    bVar8 = *(char *)((int)this + 0x308) != '\0';
    if (bVar8) {
      force_raw = true;
    }
    bVar8 = bVar8 || (*(char *)((int)this + 0x2f6) != '\0' ||
                     (bVar7 || (bVar6 || (*(char *)((int)this + 0x2f4) != '\0' ||
                                         (*(int *)((int)this + 800) != 0 ||
                                         (*(char *)((int)this + 0x328) != '\0' ||
                                         DAT_00854e6d != '\0'))))));
    iVar2 = 0;
    piVar3 = this;
    do {
      if ((*(char *)(iVar2 + 0x2e0 + (int)this) != '\0') && (*piVar3 == 2)) {
        bVar8 = true;
      }
      iVar2 = iVar2 + 1;
      piVar3 = piVar3 + 0x17;
    } while (iVar2 < 8);
    if (bVar8) {
      CVertexShader__Unk_00503ac0();
      *(int *)((int)this + 0xe54) = extraout_EAX;
      if (((bool)force_raw) && (extraout_EAX == 0)) {
        DebugTrace(unaff_ESI);
      }
    }
    if (*(int *)((int)this + 0xe54) != 0) {
      if (DAT_00854e6c != '\0') {
        CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\x01');
      }
      RenderState_Set_23_8C_Compat('\0');
      D3DStateCache__SetStateRaw(0,0xb,0);
      D3DStateCache__SetStateRaw(1,0xb,1);
      D3DStateCache__SetStateRaw(2,0xb,2);
      D3DStateCache__SetStateRaw(3,0xb,3);
      D3DStateCache__SetStateRaw(0,0x18,0);
      D3DStateCache__SetStateRaw(1,0x18,0);
      D3DStateCache__SetStateRaw(2,0x18,0);
      D3DStateCache__SetStateRaw(3,0x18,0);
      CWaterRenderSystem__Helper_00501cd0(*(int *)((int)this + 0xe54));
      CEngine__SetShaderObject(&DAT_00855bb0,*(void **)((int)this + 0xe54));
      return;
    }
  }
  if (DAT_00854e6c != '\0') {
    CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\0');
  }
  if (*(char *)((int)this + 0xe28) != '\0') {
    (**(code **)(*DAT_00888a50 + 0xb0))(DAT_00888a50,0x100,(int)this + 0x354);
    *(undefined1 *)((int)this + 0xe28) = 0;
  }
  if (*(char *)((int)this + 0xe29) != '\0') {
    (**(code **)(*DAT_00888a50 + 0xb0))(DAT_00888a50,2,(int)this + 0x394);
    *(undefined1 *)((int)this + 0xe29) = 0;
  }
  if (*(char *)((int)this + 0xe2a) != '\0') {
    uVar1 = *(uint *)((int)this + 0xe24);
    puVar4 = (undefined4 *)((int)this + 0x3d4);
    puVar5 = auStack_40;
    for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar5 = *puVar4;
      puVar4 = puVar4 + 1;
      puVar5 = puVar5 + 1;
    }
    fStack_8 = fStack_8 - (float)uVar1 * _DAT_009c742c;
    (**(code **)(*DAT_00888a50 + 0xb0))(DAT_00888a50,3,auStack_40);
    *(undefined1 *)((int)this + 0xe2a) = 0;
  }
  iVar2 = 0;
  do {
    if (*(char *)(iVar2 + 0x33c + (int)this) != '\0') {
      CDXEngine__ApplyCachedLight(this,iVar2,0);
      *(undefined1 *)(iVar2 + 0x33c + (int)this) = 0;
    }
    if (*(char *)(iVar2 + 0x344 + (int)this) != '\0') {
      (**(code **)(*DAT_00888a50 + 0xd4))
                (DAT_00888a50,iVar2,*(undefined1 *)(iVar2 + 0x2e0 + (int)this));
      *(undefined1 *)(iVar2 + 0x344 + (int)this) = 0;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 < 8);
  if (*(char *)((int)this + 0x34c) != '\0') {
    RenderState_Set(0x8b,*(int *)((int)this + 0x2e8));
    *(undefined1 *)((int)this + 0x34c) = 0;
  }
  if (*(char *)((int)this + 0xe2b) != '\0') {
    RenderState_Set(0x24,*(int *)((int)this + 0xe1c));
    *(undefined1 *)((int)this + 0xe2b) = 0;
  }
  if (*(char *)((int)this + 0xe2c) != '\0') {
    RenderState_Set(0x25,*(int *)((int)this + 0xe20));
    *(undefined1 *)((int)this + 0xe2c) = 0;
  }
  if (*(char *)((int)this + 0xe2d) != '\0') {
    RenderState_Set(0x26,*(int *)((int)this + 0x2f0));
    *(undefined1 *)((int)this + 0xe2d) = 0;
  }
  if (*(char *)((int)this + 0xe5c) != '\0') {
    if (*(int *)((int)this + 0xe14) != 0) {
      CEngine__SetVertexShaderHandleRaw(&DAT_00855bb0,*(int *)((int)this + 0xe14));
    }
    *(undefined1 *)((int)this + 0xe5c) = 0;
  }
  *(undefined1 *)((int)this + 0x34f) = 0;
  return;
}
