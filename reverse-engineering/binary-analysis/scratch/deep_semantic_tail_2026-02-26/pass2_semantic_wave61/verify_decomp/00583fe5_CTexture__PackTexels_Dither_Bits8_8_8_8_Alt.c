/* address: 0x00583fe5 */
/* name: CTexture__PackTexels_Dither_Bits8_8_8_8_Alt */
/* signature: void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_8_Alt(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__PackTexels_Dither_Bits8_8_8_8_Alt
          (void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
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
  puVar4 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_14 = CONCAT22(local_14._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_14;
  local_c = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar3 = 0;
    do {
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (local_c & 3) * 4);
      *puVar4 = (((int)ROUND(*(float *)(iVar3 + 8 + param_3) * _DAT_005e9f1c + fVar1) & 0xffU |
                 (int)ROUND(*(float *)(iVar3 + 0xc + param_3) * _DAT_005e9f1c + fVar1) << 8) << 8 |
                (int)ROUND(*(float *)(iVar3 + 4 + param_3) * _DAT_005e9f1c + fVar1) & 0xffU) << 8 |
                (int)ROUND(*(float *)(iVar3 + param_3) * _DAT_005e9f1c + fVar1) & 0xffU;
      puVar4 = puVar4 + 1;
      local_c = local_c + 1;
      iVar3 = iVar3 + 0x10;
    } while (local_c < *(uint *)((int)this + 0x1060));
  }
  return;
}
