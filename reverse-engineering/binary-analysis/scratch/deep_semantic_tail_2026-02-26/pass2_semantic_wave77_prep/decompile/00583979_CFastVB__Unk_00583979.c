/* address: 0x00583979 */
/* name: CFastVB__Unk_00583979 */
/* signature: void __thiscall CFastVB__Unk_00583979(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_00583979(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  float fVar2;
  int iVar3;
  float *pfVar4;
  ushort *puVar5;
  int iVar6;
  int unaff_EDI;
  uint uVar7;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  uVar7 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar5 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar3 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar6 = 0;
    do {
      fVar2 = *(float *)(iVar3 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar7 & 3) * 4);
      pfVar4 = (float *)(param_3 + iVar6);
      iVar1 = iVar6 + 0xc;
      iVar6 = iVar6 + 0x10;
      *puVar5 = (ushort)(((int)ROUND(*(float *)(iVar1 + param_3) * _DAT_005e9f08 + fVar2) & 0xffU)
                        << 8) |
                (ushort)(int)ROUND((*pfVar4 * _DAT_005e72dc +
                                   pfVar4[1] * _DAT_005e72e0 + pfVar4[2] * _DAT_005e72e4) *
                                   _DAT_005e9f08 + fVar2);
      puVar5 = puVar5 + 1;
      uVar7 = uVar7 + 1;
    } while (uVar7 < *(uint *)((int)this + 0x1060));
  }
  return;
}
