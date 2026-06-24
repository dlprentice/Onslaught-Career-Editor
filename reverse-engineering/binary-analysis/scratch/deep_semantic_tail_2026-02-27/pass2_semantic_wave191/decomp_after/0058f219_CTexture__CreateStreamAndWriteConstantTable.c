/* address: 0x0058f219 */
/* name: CTexture__CreateStreamAndWriteConstantTable */
/* signature: int __thiscall CTexture__CreateStreamAndWriteConstantTable(void * this, void * param_1, void * param_2) */


int __thiscall CTexture__CreateStreamAndWriteConstantTable(void *this,void *param_1,void *param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 *puVar5;
  int *local_8;

  local_8 = this;
  iVar1 = CTexture__CreateMemoryWriteStream(*(int *)((int)this + 0x5c) << 2,&local_8);
  if (-1 < iVar1) {
    uVar2 = (**(code **)(*local_8 + 0x10))(local_8);
    puVar5 = *(undefined4 **)((int)this + 0x58);
    puVar3 = (undefined4 *)(**(code **)(*local_8 + 0xc))(local_8);
    for (uVar4 = uVar2 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *puVar3 = *puVar5;
      puVar5 = puVar5 + 1;
      puVar3 = puVar3 + 1;
    }
    for (uVar2 = uVar2 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
      *(undefined1 *)puVar3 = *(undefined1 *)puVar5;
      puVar5 = (undefined4 *)((int)puVar5 + 1);
      puVar3 = (undefined4 *)((int)puVar3 + 1);
    }
    *(int **)param_1 = local_8;
    iVar1 = 0;
  }
  return iVar1;
}
