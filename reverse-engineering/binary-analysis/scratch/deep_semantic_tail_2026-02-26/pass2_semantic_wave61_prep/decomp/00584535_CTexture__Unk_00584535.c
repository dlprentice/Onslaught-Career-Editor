/* address: 0x00584535 */
/* name: CTexture__Unk_00584535 */
/* signature: void __thiscall CTexture__Unk_00584535(void * this, void * param_1, uint param_2, uint param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_00584535(void *this,void *param_1,uint param_2,uint param_3,int param_4)

{
  float fVar1;
  int iVar2;
  uint uVar3;
  undefined2 *puVar4;
  int unaff_EDI;
  undefined2 in_FPUControlWord;
  float local_2c;
  float local_28;
  undefined4 local_c;

  uVar3 = 0;
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar4 = (undefined2 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  iVar2 = *(int *)((int)this + 0x34);
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_c;
  if (*(int *)((int)this + 0x1060) != 0) {
    do {
      CTexture__Helper_00575d99();
      fVar1 = *(float *)(iVar2 + ((param_2 & 3) + ((uint)param_1 & 3) * 8) * 4 + (uVar3 & 3) * 4);
      *puVar4 = CONCAT11((char)(int)ROUND(local_28 * _DAT_005e9f1c + fVar1),
                         (char)(int)ROUND(local_2c * _DAT_005e9f1c + fVar1));
      puVar4 = puVar4 + 1;
      uVar3 = uVar3 + 1;
    } while (uVar3 < *(uint *)((int)this + 0x1060));
  }
  return;
}
