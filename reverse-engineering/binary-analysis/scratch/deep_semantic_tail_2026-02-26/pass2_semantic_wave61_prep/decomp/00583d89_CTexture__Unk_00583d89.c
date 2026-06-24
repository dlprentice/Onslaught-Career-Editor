/* address: 0x00583d89 */
/* name: CTexture__Unk_00583d89 */
/* signature: void __thiscall CTexture__Unk_00583d89(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_00583d89(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  ushort *puVar3;
  uint uVar4;
  int iVar5;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  iVar5 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar3 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  uVar4 = 0;
  if (*(int *)((int)this + 0x1060) != 0) {
    do {
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar4 & 3) * 4);
      *puVar3 = (ushort)(((int)ROUND(*(float *)(iVar5 + 4 + param_3) * _DAT_005e9f04 + fVar1) &
                          0x1fU | (int)ROUND(*(float *)(iVar5 + 0xc + param_3) * _DAT_005e9ef8 +
                                             fVar1) << 5) << 5) |
                (ushort)(int)ROUND(*(float *)(iVar5 + param_3) * _DAT_005e9f04 + fVar1) & 0x1f;
      puVar3 = puVar3 + 1;
      uVar4 = uVar4 + 1;
      iVar5 = iVar5 + 0x10;
    } while (uVar4 < *(uint *)((int)this + 0x1060));
  }
  return;
}
