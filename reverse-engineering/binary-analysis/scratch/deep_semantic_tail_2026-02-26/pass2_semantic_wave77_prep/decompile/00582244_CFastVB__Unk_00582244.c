/* address: 0x00582244 */
/* name: CFastVB__Unk_00582244 */
/* signature: void __thiscall CFastVB__Unk_00582244(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_00582244(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  int unaff_EDI;
  uint uVar5;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  uVar5 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar4 = (undefined1 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    iVar3 = 0;
    do {
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar5 & 3) * 4);
      *puVar4 = (char)(int)ROUND(*(float *)(iVar3 + 8 + param_3) * _DAT_005e9f08 + fVar1);
      puVar4[1] = (char)(int)ROUND(*(float *)(iVar3 + 4 + param_3) * _DAT_005e9f08 + fVar1);
      puVar4[2] = (char)(int)ROUND(*(float *)(iVar3 + param_3) * _DAT_005e9f08 + fVar1);
      puVar4 = puVar4 + 3;
      uVar5 = uVar5 + 1;
      iVar3 = iVar3 + 0x10;
    } while (uVar5 < *(uint *)((int)this + 0x1060));
  }
  return;
}
