/* address: 0x00584831 */
/* name: CDXTexture__PackTexels_CopyRaw32 */
/* signature: void __thiscall CDXTexture__PackTexels_CopyRaw32(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CDXTexture__PackTexels_CopyRaw32(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  undefined4 *puVar1;
  uint uVar2;
  int unaff_ESI;

  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_ESI);
  }
  puVar1 = (undefined4 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  uVar2 = 0;
  if (*(uint *)((int)this + 0x1060) != 0) {
    do {
      *puVar1 = *(undefined4 *)param_3;
      puVar1 = puVar1 + 1;
      uVar2 = uVar2 + 1;
      param_3 = param_3 + 0x10;
    } while (uVar2 < *(uint *)((int)this + 0x1060));
  }
  return;
}
