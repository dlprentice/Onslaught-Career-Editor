/* address: 0x00583670 */
/* name: CDXTexture__PackTexels_Dither_PaletteIndexA8 */
/* signature: void __thiscall CDXTexture__PackTexels_Dither_PaletteIndexA8(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__PackTexels_Dither_PaletteIndexA8
          (void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  float fVar2;
  float *pfVar3;
  ushort *puVar4;
  uint uVar5;
  float *pfVar6;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  uint local_1c;
  float local_18;
  undefined4 local_14;
  int local_10;
  uint local_c;

  uVar5 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar4 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar1 = *(int *)((int)this + 0x34);
  local_14 = CONCAT22(local_14._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_14;
  if (*(int *)((int)this + 0x1060) != 0) {
    local_10 = 0;
    do {
      local_1c = 0;
      local_c = 0;
      pfVar3 = (float *)(param_3 + local_10);
      local_18 = 3.4028235e+38;
      pfVar6 = (float *)((int)this + 0x40);
      do {
        fVar2 = (*pfVar3 - pfVar6[-2]) * (*pfVar3 - pfVar6[-2]) +
                (pfVar3[1] - pfVar6[-1]) * (pfVar3[1] - pfVar6[-1]) +
                (pfVar3[2] - *pfVar6) * (pfVar3[2] - *pfVar6);
        if (fVar2 < local_18) {
          local_1c = local_c;
          local_18 = fVar2;
        }
        local_c = local_c + 1;
        pfVar6 = pfVar6 + 4;
      } while (local_c < 0x100);
      local_10 = local_10 + 0x10;
      *puVar4 = (ushort)(byte)(int)ROUND(pfVar3[3] * _DAT_005e9f08 +
                                         *(float *)(iVar1 + ((param_2 & 3) + ((uint)param_1 & 3) * 8
                                                            ) * 4 + (uVar5 & 3) * 4)) << 8 |
                (ushort)local_1c;
      puVar4 = puVar4 + 1;
      uVar5 = uVar5 + 1;
    } while (uVar5 < *(uint *)((int)this + 0x1060));
  }
  return;
}
