/* address: 0x005833a6 */
/* name: CDXTexture__Unk_005833a6 */
/* signature: void __thiscall CDXTexture__Unk_005833a6(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__Unk_005833a6(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float *pfVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  float fVar5;
  int iVar6;
  int iVar7;
  uint *puVar8;
  uint uVar9;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  undefined4 local_10;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar8 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar6 = *(int *)((int)this + 0x34);
  local_10 = CONCAT22(local_10._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_10;
  uVar9 = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar7 = 0;
    do {
      fVar5 = *(float *)(iVar6 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar9 & 3) * 4);
      iVar2 = iVar7 + 8;
      iVar3 = iVar7 + 4;
      pfVar1 = (float *)(iVar7 + param_3);
      iVar4 = iVar7 + 0xc;
      iVar7 = iVar7 + 0x10;
      *puVar8 = (((int)ROUND(*(float *)(iVar4 + param_3) * _DAT_005e9318 + fVar5) << 10 |
                 (int)ROUND(*pfVar1 * _DAT_005e9f14 + fVar5)) << 10 |
                (int)ROUND(*(float *)(iVar3 + param_3) * _DAT_005e9f14 + fVar5)) << 10 |
                (int)ROUND(*(float *)(iVar2 + param_3) * _DAT_005e9f14 + fVar5);
      puVar8 = puVar8 + 1;
      uVar9 = uVar9 + 1;
    } while (uVar9 < *(uint *)((int)this + 0x1060));
  }
  return;
}
