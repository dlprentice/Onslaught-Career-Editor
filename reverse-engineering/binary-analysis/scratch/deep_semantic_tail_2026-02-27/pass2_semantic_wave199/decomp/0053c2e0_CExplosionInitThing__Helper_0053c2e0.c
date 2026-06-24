/* address: 0x0053c2e0 */
/* name: CExplosionInitThing__Helper_0053c2e0 */
/* signature: void __thiscall CExplosionInitThing__Helper_0053c2e0(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CExplosionInitThing__Helper_0053c2e0(void *this,void *param_1,int param_2)

{
  float fVar1;
  byte *pbVar2;
  undefined4 uVar3;
  float *pfVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  undefined4 *unaff_EBP;
  int unaff_ESI;
  undefined4 *puVar9;
  undefined4 *puVar10;
  int iStack_2c;
  int local_10 [2];
  longlong local_8;

  puVar9 = this;
  for (iVar6 = 0xf00; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar9 = 0;
    puVar9 = puVar9 + 1;
  }
  iStack_2c = 0xf;
  puVar9 = (undefined4 *)((int)this + 0x1a00);
  for (iVar6 = 0x280; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar9 = 0x2020202;
    puVar9 = puVar9 + 1;
  }
  CByteSprite__DrawFrame(0,0);
  iVar6 = *(int *)((int)param_1 + 0x2b8);
  if (iVar6 != 0) {
    puVar9 = *(undefined4 **)(iVar6 + 0x1c);
    *(undefined4 **)(iVar6 + 0x24) = puVar9;
    if (puVar9 == (undefined4 *)0x0) {
      pfVar4 = (float *)0x0;
    }
    else {
      pfVar4 = (float *)*puVar9;
    }
    while (pfVar4 != (float *)0x0) {
      for (fVar1 = -*pfVar4; fVar1 < _DAT_005d856c; fVar1 = fVar1 + _DAT_005d85e0) {
      }
      for (; _DAT_005d85e0 < fVar1; fVar1 = fVar1 - _DAT_005d85e0) {
      }
      iStack_2c = 0xf;
      local_8 = (longlong)ROUND(fVar1 * _DAT_005d9288 * _DAT_005d8c28);
      uVar3 = (int)local_8;
      CByteSprite__DrawFrame(1,(int)local_8);
      local_8 = (longlong)ROUND(pfVar4[1] * _DAT_005d8c64);
      iStack_2c = 0xf - (int)local_8;
      CByteSprite__DrawFrame(2,uVar3);
      puVar9 = *(undefined4 **)(*(int *)(iVar6 + 0x24) + 4);
      *(undefined4 **)(iVar6 + 0x24) = puVar9;
      if (puVar9 == (undefined4 *)0x0) {
        pfVar4 = (float *)0x0;
      }
      else {
        pfVar4 = (float *)*puVar9;
      }
    }
  }
  iStack_2c = 0x53c41e;
  piVar5 = CDXTexture__GetAnimatedFrame
                     (*(void **)((int)this + *(int *)((int)this + 0x3c10) * 4 + 0x3c00));
  iStack_2c = 0x800;
  iVar6 = (**(code **)(*piVar5 + 0x4c))(piVar5,0,local_10,0);
  if (-1 < iVar6) {
    uVar8 = DAT_00650424 * 2;
    puVar9 = unaff_EBP;
    for (uVar7 = uVar8 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
      *puVar9 = 0;
      puVar9 = puVar9 + 1;
    }
    for (uVar8 = uVar8 & 3; uVar8 != 0; uVar8 = uVar8 - 1) {
      *(undefined1 *)puVar9 = 0;
      puVar9 = (undefined4 *)((int)puVar9 + 1);
    }
    puVar9 = (undefined4 *)((int)unaff_EBP + unaff_ESI);
    if (DAT_00650424 < 0x200) {
      iVar6 = (int)(0x200 / (ulonglong)DAT_00650424);
    }
    else {
      iVar6 = 1;
    }
    local_10[0] = 0x1e;
    pbVar2 = this;
    uVar8 = DAT_00650424;
    uVar7 = DAT_00650424;
    puVar10 = puVar9;
    do {
      for (; uVar8 != 0; uVar8 = uVar8 - 1) {
        *(undefined2 *)puVar9 = *(undefined2 *)((int)&iStack_2c + (uint)*pbVar2 * 2);
        pbVar2 = pbVar2 + iVar6;
        puVar9 = (undefined4 *)((int)puVar9 + 2);
        uVar7 = DAT_00650424;
      }
      puVar9 = (undefined4 *)((int)puVar10 + unaff_ESI);
      local_10[0] = local_10[0] + -1;
      uVar8 = uVar7;
      puVar10 = puVar9;
    } while (local_10[0] != 0);
    for (iVar6 = DAT_00650428 + -0x1f; iVar6 != 0; iVar6 = iVar6 + -1) {
      puVar10 = puVar9;
      for (uVar8 = uVar7 * 2 >> 2; uVar8 != 0; uVar8 = uVar8 - 1) {
        *puVar10 = 0;
        puVar10 = puVar10 + 1;
      }
      for (uVar8 = uVar7 * 2 & 3; uVar8 != 0; uVar8 = uVar8 - 1) {
        *(undefined1 *)puVar10 = 0;
        puVar10 = (undefined4 *)((int)puVar10 + 1);
      }
      puVar9 = (undefined4 *)((int)puVar9 + unaff_ESI);
      uVar7 = DAT_00650424;
    }
    piVar5 = CDXTexture__GetAnimatedFrame
                       (*(void **)((int)this + *(int *)((int)this + 0x3c10) * 4 + 0x3c00));
    (**(code **)(*piVar5 + 0x50))(piVar5,0);
  }
  return;
}
