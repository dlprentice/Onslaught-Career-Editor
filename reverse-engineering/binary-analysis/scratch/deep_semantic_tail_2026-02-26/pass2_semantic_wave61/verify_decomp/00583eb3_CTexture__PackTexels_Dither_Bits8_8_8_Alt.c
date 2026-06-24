/* address: 0x00583eb3 */
/* name: CTexture__PackTexels_Dither_Bits8_8_8_Alt */
/* signature: void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_Alt(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__PackTexels_Dither_Bits8_8_8_Alt
          (void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float *pfVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  int iVar5;
  uint *puVar6;
  int iVar7;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  undefined1 local_28;
  undefined4 local_10;
  uint local_c;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar6 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar5 = *(int *)((int)this + 0x34);
  local_10 = CONCAT22(local_10._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_10;
  local_c = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar7 = 0;
    do {
      fVar4 = *(float *)(iVar5 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (local_c & 3) * 4);
      pfVar1 = (float *)(iVar7 + param_3);
      iVar2 = iVar7 + 4;
      iVar3 = iVar7 + 0xc;
      iVar7 = iVar7 + 0x10;
      local_28 = (undefined1)(int)ROUND(*(float *)(iVar2 + param_3) * _DAT_005e9f1c + fVar4);
      *puVar6 = (uint)CONCAT11((char)(int)ROUND(*(float *)(iVar3 + param_3) * _DAT_005e9f08 + fVar4)
                               ,local_28) << 8 | (int)ROUND(*pfVar1 * _DAT_005e9f1c + fVar4) & 0xffU
      ;
      puVar6 = puVar6 + 1;
      local_c = local_c + 1;
    } while (local_c < *(uint *)((int)this + 0x1060));
  }
  return;
}
