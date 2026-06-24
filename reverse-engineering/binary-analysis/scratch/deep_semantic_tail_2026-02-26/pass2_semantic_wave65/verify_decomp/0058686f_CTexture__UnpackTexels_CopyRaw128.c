/* address: 0x0058686f */
/* name: CTexture__UnpackTexels_CopyRaw128 */
/* signature: void __thiscall CTexture__UnpackTexels_CopyRaw128(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CTexture__UnpackTexels_CopyRaw128(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;
  uint unaff_EDI;
  undefined4 *puVar4;

  puVar3 = (undefined4 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  puVar4 = (undefined4 *)param_3;
  for (uVar1 = (uint)(*(int *)((int)this + 0x1060) << 4) >> 2; uVar1 != 0; uVar1 = uVar1 - 1) {
    *puVar4 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  }
  for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(undefined1 *)puVar4 = *(undefined1 *)puVar3;
    puVar3 = (undefined4 *)((int)puVar3 + 1);
    puVar4 = (undefined4 *)((int)puVar4 + 1);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,param_3,unaff_EDI);
  }
  return;
}
