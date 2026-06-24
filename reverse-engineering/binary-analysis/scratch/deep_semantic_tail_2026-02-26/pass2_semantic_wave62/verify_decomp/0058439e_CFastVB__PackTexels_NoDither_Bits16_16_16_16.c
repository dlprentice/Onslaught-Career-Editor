/* address: 0x0058439e */
/* name: CFastVB__PackTexels_NoDither_Bits16_16_16_16 */
/* signature: void __thiscall CFastVB__PackTexels_NoDither_Bits16_16_16_16(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__PackTexels_NoDither_Bits16_16_16_16
          (void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  uint *puVar5;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  int local_18;
  undefined4 local_14;
  uint local_c;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar5 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_14 = CONCAT22(local_14._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_14;
  local_c = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    local_18 = 0;
    do {
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (local_c & 3) * 4);
      fVar3 = *(float *)(local_18 + param_3) * _DAT_005e9f20;
      fVar4 = *(float *)(local_18 + 4 + param_3) * _DAT_005e9f20;
      puVar5[1] = (int)ROUND(*(float *)(local_18 + 0xc + param_3) * _DAT_005e9f20 + fVar1) << 0x10 |
                  (int)ROUND(*(float *)(local_18 + 8 + param_3) * _DAT_005e9f20 + fVar1) & 0xffffU;
      *puVar5 = (int)ROUND(fVar4 + fVar1) << 0x10 | (int)ROUND(fVar3 + fVar1) & 0xffffU;
      puVar5 = puVar5 + 2;
      local_c = local_c + 1;
      local_18 = local_18 + 0x10;
    } while (local_c < *(uint *)((int)this + 0x1060));
  }
  return;
}
