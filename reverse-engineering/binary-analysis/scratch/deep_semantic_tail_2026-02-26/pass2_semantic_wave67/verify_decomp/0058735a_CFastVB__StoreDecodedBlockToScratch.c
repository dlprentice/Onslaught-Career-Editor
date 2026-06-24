/* address: 0x0058735a */
/* name: CFastVB__StoreDecodedBlockToScratch */
/* signature: void __thiscall CFastVB__StoreDecodedBlockToScratch(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CFastVB__StoreDecodedBlockToScratch(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  int iVar1;
  uint uVar2;
  uint unaff_EDI;
  undefined4 *puVar3;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  iVar1 = CFastVB__Helper_00586f37
                    (this,(int)param_1 + *(int *)((int)this + 0x103c),
                     param_2 + *(int *)((int)this + 0x1048),
                     (uint)(*(int *)((int)this + 0x1090) != *(int *)((int)this + 0x1060)),unaff_EDI)
  ;
  if (-1 < iVar1) {
    puVar3 = (undefined4 *)
             ((*(int *)((int)this + 0x1038) - *(int *)((int)this + 0x1078)) * 0x10 +
             *(int *)((int)this + 0x1074));
    for (uVar2 = (uint)(*(int *)((int)this + 0x1060) << 4) >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
      *puVar3 = *(undefined4 *)param_3;
      param_3 = (int)(param_3 + 4);
      puVar3 = puVar3 + 1;
    }
    for (iVar1 = 0; iVar1 != 0; iVar1 = iVar1 + -1) {
      *(undefined1 *)puVar3 = *(undefined1 *)param_3;
      param_3 = (int)(param_3 + 1);
      puVar3 = (undefined4 *)((int)puVar3 + 1);
    }
    *(undefined4 *)((int)this + 0x1094) = 1;
  }
  return;
}
