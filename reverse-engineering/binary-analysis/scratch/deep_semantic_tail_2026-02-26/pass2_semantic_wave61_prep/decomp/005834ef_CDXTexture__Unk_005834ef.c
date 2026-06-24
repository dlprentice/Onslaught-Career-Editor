/* address: 0x005834ef */
/* name: CDXTexture__Unk_005834ef */
/* signature: void __thiscall CDXTexture__Unk_005834ef(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__Unk_005834ef(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  float fVar4;
  int iVar5;
  float fVar6;
  int iVar7;
  uint *puVar8;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  undefined4 local_14;
  uint local_c;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar8 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar5 = *(int *)((int)this + 0x34);
  local_14 = CONCAT22(local_14._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_14;
  local_c = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar7 = 0;
    do {
      fVar4 = *(float *)(iVar5 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (local_c & 3) * 4);
      uVar1 = (uint)ROUND(*(float *)(iVar7 + param_3) * _DAT_005e9f18 + fVar4);
      uVar2 = (uint)ROUND(*(float *)(iVar7 + 4 + param_3) * _DAT_005e9f18 + fVar4);
      uVar3 = (uint)ROUND(*(float *)(iVar7 + 8 + param_3) * _DAT_005e9f18 + fVar4);
      fVar6 = *(float *)(iVar7 + 0xc + param_3) * _DAT_005e9f18;
      *puVar8 = uVar2 << 0x10 | uVar1;
      puVar8[1] = (((int)ROUND(fVar6 + fVar4) << 0x10 | uVar3) >> 0x10 | (int)uVar2 >> 0x1f) << 0x10
                  | (uVar3 << 0x10 | uVar2) >> 0x10 | (int)uVar1 >> 0x1f;
      puVar8 = puVar8 + 2;
      local_c = local_c + 1;
      iVar7 = iVar7 + 0x10;
    } while (local_c < *(uint *)((int)this + 0x1060));
  }
  return;
}
