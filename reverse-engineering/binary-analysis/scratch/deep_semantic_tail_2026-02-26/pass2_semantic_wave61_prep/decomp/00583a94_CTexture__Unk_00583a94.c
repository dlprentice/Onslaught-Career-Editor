/* address: 0x00583a94 */
/* name: CTexture__Unk_00583a94 */
/* signature: void __thiscall CTexture__Unk_00583a94(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_00583a94(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  float *pfVar3;
  byte *pbVar4;
  int iVar5;
  int unaff_EDI;
  uint uVar6;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  uVar6 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  pbVar4 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar5 = 0;
    do {
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar6 & 3) * 4);
      pfVar3 = (float *)(param_3 + iVar5);
      *pbVar4 = (char)(int)ROUND(*(float *)(iVar5 + 0xc + param_3) * _DAT_005e9f04 + fVar1) << 4 |
                (byte)(int)ROUND((*pfVar3 * _DAT_005e72dc +
                                 pfVar3[1] * _DAT_005e72e0 + pfVar3[2] * _DAT_005e72e4) *
                                 _DAT_005e9f04 + fVar1);
      pbVar4 = pbVar4 + 1;
      uVar6 = uVar6 + 1;
      iVar5 = iVar5 + 0x10;
    } while (uVar6 < *(uint *)((int)this + 0x1060));
  }
  return;
}
