/* address: 0x005848e3 */
/* name: CDXTexture__PackTexels_CopyRaw128 */
/* signature: void __thiscall CDXTexture__PackTexels_CopyRaw128(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CDXTexture__PackTexels_CopyRaw128(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint uVar1;
  int iVar2;
  int unaff_EDI;
  undefined4 *puVar3;

  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  puVar3 = (undefined4 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  for (uVar1 = (uint)(*(int *)((int)this + 0x1060) << 4) >> 2; uVar1 != 0; uVar1 = uVar1 - 1) {
    *puVar3 = *(undefined4 *)param_3;
    param_3 = (int)(param_3 + 4);
    puVar3 = puVar3 + 1;
  }
  for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(undefined1 *)puVar3 = *(undefined1 *)param_3;
    param_3 = (int)(param_3 + 1);
    puVar3 = (undefined4 *)((int)puVar3 + 1);
  }
  return;
}
