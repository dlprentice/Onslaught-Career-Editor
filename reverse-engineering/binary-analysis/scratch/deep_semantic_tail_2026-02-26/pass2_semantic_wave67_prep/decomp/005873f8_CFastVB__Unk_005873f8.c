/* address: 0x005873f8 */
/* name: CFastVB__Unk_005873f8 */
/* signature: void __thiscall CFastVB__Unk_005873f8(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CFastVB__Unk_005873f8(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  int iVar1;
  uint uVar2;
  uint unaff_EBX;
  undefined4 *puVar3;
  undefined4 *puVar4;

  iVar1 = CFastVB__Helper_00586f37
                    (this,(int)param_1 + *(int *)((int)this + 0x103c),
                     param_2 + *(int *)((int)this + 0x1048),1,unaff_EBX);
  if (-1 < iVar1) {
    puVar3 = (undefined4 *)
             ((*(int *)((int)this + 0x1038) - *(int *)((int)this + 0x1078)) * 0x10 +
             *(int *)((int)this + 0x1074));
    puVar4 = (undefined4 *)param_3;
    for (uVar2 = (uint)(*(int *)((int)this + 0x1060) << 4) >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
      *puVar4 = *puVar3;
      puVar3 = puVar3 + 1;
      puVar4 = puVar4 + 1;
    }
    for (iVar1 = 0; iVar1 != 0; iVar1 = iVar1 + -1) {
      *(undefined1 *)puVar4 = *(undefined1 *)puVar3;
      puVar3 = (undefined4 *)((int)puVar3 + 1);
      puVar4 = (undefined4 *)((int)puVar4 + 1);
    }
    if (*(int *)((int)this + 0x18) != 0) {
      CFastVB__Helper_00581e1c(this,param_3,unaff_EBX);
    }
    if (*(int *)((int)this + 0x10) != 0) {
      CTexture__Helper_0058210e(this,param_3,unaff_EBX);
    }
  }
  return;
}
