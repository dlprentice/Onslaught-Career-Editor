/* address: 0x00584936 */
/* name: CDXTexture__PackTexels_NoDither_A16L16 */
/* signature: void __thiscall CDXTexture__PackTexels_NoDither_A16L16(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__PackTexels_NoDither_A16L16
          (void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  float fVar2;
  int iVar3;
  float *pfVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  undefined2 in_FPUControlWord;
  int in_stack_ffffffe8;
  undefined4 local_c;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,in_stack_ffffffe8);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,in_stack_ffffffe8);
  }
  puVar6 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar3 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  iVar5 = 0;
  uVar7 = 0;
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    do {
      fVar2 = *(float *)(iVar3 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar7 & 3) * 4);
      pfVar4 = (float *)(param_3 + iVar5);
      iVar1 = iVar5 + 0xc;
      iVar5 = iVar5 + 0x10;
      *puVar6 = (int)ROUND(*(float *)(iVar1 + param_3) * _DAT_005e9f18 + fVar2) << 0x10 |
                (int)ROUND((*pfVar4 * _DAT_005e72dc +
                           pfVar4[1] * _DAT_005e72e0 + pfVar4[2] * _DAT_005e72e4) * _DAT_005e9f18 +
                           fVar2);
      puVar6 = puVar6 + 1;
      uVar7 = uVar7 + 1;
    } while (uVar7 < *(uint *)((int)this + 0x1060));
  }
  return;
}
