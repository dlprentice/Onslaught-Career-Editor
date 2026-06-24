/* address: 0x005832af */
/* name: CDXTexture__Unk_005832af */
/* signature: void __thiscall CDXTexture__Unk_005832af(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__Unk_005832af(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float *pfVar1;
  int iVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  uint *puVar6;
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
  puVar6 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  iVar4 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar5 = 0;
    do {
      fVar3 = *(float *)(iVar4 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar7 & 3) * 4);
      pfVar1 = (float *)(iVar5 + param_3);
      iVar2 = iVar5 + 4;
      iVar5 = iVar5 + 0x10;
      *puVar6 = (int)ROUND(*(float *)(iVar2 + param_3) * _DAT_005e9f18 + fVar3) << 0x10 |
                (int)ROUND(*pfVar1 * _DAT_005e9f18 + fVar3);
      puVar6 = puVar6 + 1;
      uVar7 = uVar7 + 1;
    } while (uVar7 < *(uint *)((int)this + 0x1060));
  }
  return;
}
