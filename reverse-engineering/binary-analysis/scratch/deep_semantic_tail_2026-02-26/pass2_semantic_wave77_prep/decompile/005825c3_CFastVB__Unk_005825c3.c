/* address: 0x005825c3 */
/* name: CFastVB__Unk_005825c3 */
/* signature: void __thiscall CFastVB__Unk_005825c3(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_005825c3(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float *pfVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  ushort *puVar7;
  int unaff_EDI;
  uint uVar8;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  uVar8 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar7 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar5 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar6 = 0;
    do {
      fVar4 = *(float *)(iVar5 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar8 & 3) * 4);
      pfVar1 = (float *)(iVar6 + param_3);
      iVar2 = iVar6 + 4;
      iVar3 = iVar6 + 8;
      iVar6 = iVar6 + 0x10;
      *puVar7 = (ushort)(((int)ROUND(*pfVar1 * _DAT_005e9f00 + fVar4) << 6 |
                         (int)ROUND(*(float *)(iVar2 + param_3) * _DAT_005e9ef8 + fVar4)) << 5) |
                (ushort)(int)ROUND(*(float *)(iVar3 + param_3) * _DAT_005e9f00 + fVar4);
      puVar7 = puVar7 + 1;
      uVar8 = uVar8 + 1;
    } while (uVar8 < *(uint *)((int)this + 0x1060));
  }
  return;
}
