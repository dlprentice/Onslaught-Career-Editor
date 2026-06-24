/* address: 0x00582bbe */
/* name: CTexture__PackTexels_Dither_Bits8 */
/* signature: void __thiscall CTexture__PackTexels_Dither_Bits8(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__PackTexels_Dither_Bits8(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  undefined1 *puVar2;
  uint uVar3;
  int unaff_EDI;
  int iVar4;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  iVar4 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar2 = (undefined1 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar1 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  uVar3 = 0;
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    do {
      *puVar2 = (char)(int)ROUND(*(float *)(iVar4 + 0xc + param_3) * _DAT_005e9f08 +
                                 *(float *)(iVar1 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 +
                                           (uVar3 & 3) * 4));
      puVar2 = puVar2 + 1;
      uVar3 = uVar3 + 1;
      iVar4 = iVar4 + 0x10;
    } while (uVar3 < *(uint *)((int)this + 0x1060));
  }
  return;
}
