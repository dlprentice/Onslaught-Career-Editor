/* address: 0x004a4810 */
/* name: CMenuItemRange__Render */
/* signature: undefined CMenuItemRange__Render(void) */


/* WARNING: Removing unreachable block (ram,0x004a4c5f) */
/* WARNING: Removing unreachable block (ram,0x004a4c6f) */
/* WARNING: Removing unreachable block (ram,0x004a4c9c) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CMenuItemRange__Render(int *param_1,int param_2)

{
  int *this;
  undefined4 *puVar1;
  char cVar2;
  int iVar3;
  void *pvVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int unaff_EBX;
  int unaff_EBP;
  float unaff_ESI;
  int iVar8;
  float fVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  short *psVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  int *local_2c;
  float local_1c;
  undefined8 local_10;
  int aiStack_8 [2];

  CMenuItemDropdown__ClearPending();
  cVar2 = DAT_0082b4e8;
  this = param_1 + 2;
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  puVar1 = (undefined4 *)*this;
  local_1c = (float)param_1[7];
  fVar9 = (float)param_1[8];
  iVar8 = 0x20;
  param_1[4] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*puVar1;
  }
  while (piVar5 != (int *)0x0) {
    iVar3 = (**(code **)(*piVar5 + 0x18))();
    iVar8 = iVar8 + iVar3;
    puVar1 = *(undefined4 **)(param_1[4] + 4);
    param_1[4] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
  }
  local_10 = CONCAT44(local_10._4_4_,iVar8 + -0x20);
  local_2c = (int *)((fVar9 - (float)(iVar8 + -0x20) * _DAT_005d85ec) - _DAT_005d85d4);
  if (param_1[10] != 0) {
    psVar12 = (short *)param_1[1];
    piVar5 = (int *)&local_10;
    pvVar4 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar4,psVar12,piVar5);
    iVar3 = (int)(float)local_10;
    iVar8 = 0;
    piVar5 = CSPtrSet__First(this);
    while (piVar5 != (int *)0x0) {
      iVar6 = (**(code **)(*piVar5 + 0x14))();
      if (iVar8 < iVar6) {
        iVar8 = iVar6;
      }
      piVar5 = CSPtrSet__Next(this);
    }
    if (iVar3 < iVar8) {
      iVar3 = iVar8;
    }
    puVar1 = (undefined4 *)*this;
    local_10._4_4_ = (undefined4)((ulonglong)local_10 >> 0x20);
    param_1[4] = (int)puVar1;
    local_10 = CONCAT44(local_10._4_4_,(float)(iVar3 + 0x10) * _DAT_005dc240);
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
    while (piVar5 != (int *)0x0) {
      (**(code **)(*piVar5 + 0x18))();
      puVar1 = *(undefined4 **)(param_1[4] + 4);
      param_1[4] = (int)puVar1;
      if (puVar1 == (undefined4 *)0x0) {
        piVar5 = (int *)0x0;
      }
      else {
        piVar5 = (int *)*puVar1;
      }
    }
    local_10 = (longlong)ROUND(local_1c - (float)local_10 * _DAT_005d85ec);
    CMessageLog__Unk_004b9010();
  }
  if ((cVar2 == '\0') && (psVar12 = (short *)param_1[1], psVar12 != (short *)0x0)) {
    piVar5 = aiStack_8;
    pvVar4 = CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__GetTextExtent(pvVar4,psVar12,piVar5);
    uVar14 = 0x3f800000;
    iVar8 = param_1[1];
    uVar13 = 0;
    uVar11 = 0;
    uVar10 = 0xff505050;
    fVar9 = local_1c - (float)(aiStack_8[0] / 2);
    local_10 = CONCAT44(local_10._4_4_,fVar9);
    piVar5 = local_2c;
    CPlatform__Font(&DAT_0088a0a8,0);
    CDXFont__DrawText(fVar9,piVar5,uVar10,iVar8,uVar11,uVar13,uVar14);
    local_2c = (int *)((float)local_2c + _DAT_005db1e4);
  }
  puVar1 = (undefined4 *)*this;
  iVar8 = 0;
  iVar3 = 0;
  param_1[4] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*puVar1;
  }
  while (piVar5 != (int *)0x0) {
    iVar6 = (**(code **)(*piVar5 + 0x14))();
    if (iVar8 < iVar6) {
      iVar8 = iVar6;
    }
    puVar1 = *(undefined4 **)(param_1[4] + 4);
    param_1[4] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
  }
  DAT_00704a88 = 0;
  if (param_1[9] == 0) {
    piVar5 = CTexture__FindTexture(s_FrontEnd_v2_FE_Blank_tga_00629f68,4,0,1,0,1);
    param_1[9] = (int)piVar5;
    puVar1 = (undefined4 *)*this;
    param_1[4] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
    while (piVar5 != (int *)0x0) {
      (**(code **)(*piVar5 + 0x34))();
      puVar1 = *(undefined4 **)(param_1[4] + 4);
      param_1[4] = (int)puVar1;
      if (puVar1 == (undefined4 *)0x0) {
        piVar5 = (int *)0x0;
      }
      else {
        piVar5 = (int *)*puVar1;
      }
    }
  }
  puVar1 = (undefined4 *)*this;
  param_1[4] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*puVar1;
  }
  while (piVar5 != (int *)0x0) {
    iVar8 = CPauseMenu__Unk_004d05c0(param_2);
    if (((char)iVar8 == '\0') || (cVar2 = (**(code **)(*param_1 + 0xc))(), cVar2 != '\0')) {
      piVar7 = (int *)CUnit__Unk_004e5c90(this,(void *)param_1[6],unaff_EBX);
      cVar2 = (**(code **)(*piVar7 + 0x24))();
      if (cVar2 == '\0') {
        iVar8 = (**(code **)(*piVar5 + 0x18))();
        local_10 = CONCAT44(local_10._4_4_,iVar8);
        cVar2 = CMenuItem__IsMouseInBounds(0,local_2c,0x44200000,(float)iVar8 + (float)local_2c);
        if (cVar2 != '\0') {
          param_1[6] = iVar3;
        }
      }
    }
    iVar8 = param_1[6];
    D3DStateCache__SetSlotMode4or5(0);
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    fVar9 = local_1c;
    (**(code **)(*piVar5 + 0x10))(local_1c,local_2c,iVar3 == iVar8);
    iVar8 = CPauseMenu__Unk_004d05c0(aiStack_8[0]);
    if (((char)iVar8 == '\0') || (cVar2 = (**(code **)(*local_2c + 0xc))(), cVar2 != '\0')) {
      piVar7 = (int *)CUnit__Unk_004e5c90(this,(void *)local_2c[6],(int)fVar9);
      cVar2 = (**(code **)(*piVar7 + 0x24))();
      if (cVar2 == '\0') {
        local_1c = (float)(**(code **)(*piVar5 + 0x18))();
        cVar2 = CMenuItem__IsMouseClicked(0,local_2c,0x44200000,(float)(int)local_1c + unaff_ESI);
        if (cVar2 != '\0') {
          local_2c[6] = unaff_EBP;
        }
      }
    }
    cVar2 = (**(code **)(*piVar5 + 0x28))();
    if (cVar2 != '\0') {
      DAT_00704a88 = 1;
    }
    iVar8 = (**(code **)(*piVar5 + 0x18))();
    local_10 = CONCAT44(local_10._4_4_,iVar8);
    iVar3 = iVar3 + 1;
    puVar1 = *(undefined4 **)(param_1[4] + 4);
    local_2c = (int *)((float)iVar8 + (float)local_2c);
    param_1[4] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
  }
  CMenuItemDropdown__ProcessPending();
  return param_1[1];
}
