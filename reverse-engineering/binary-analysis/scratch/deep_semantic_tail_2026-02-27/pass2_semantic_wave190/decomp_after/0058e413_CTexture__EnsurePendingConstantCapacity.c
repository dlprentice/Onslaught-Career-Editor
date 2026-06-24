/* address: 0x0058e413 */
/* name: CTexture__EnsurePendingConstantCapacity */
/* signature: int __thiscall CTexture__EnsurePendingConstantCapacity(void * this, int param_1, int param_2) */


int __thiscall CTexture__EnsurePendingConstantCapacity(void *this,int param_1,int param_2)

{
  uint uVar1;
  undefined4 *extraout_EAX;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;

  uVar3 = *(uint *)((int)this + 0x60);
  uVar1 = *(int *)((int)this + 0x5c) + param_1;
  if (uVar3 < uVar1) {
    if (uVar3 == 0) {
      uVar3 = 0x100;
    }
    if (uVar3 < uVar1) {
      do {
        uVar3 = uVar3 * 2;
      } while (uVar3 < (uint)(*(int *)((int)this + 0x5c) + param_1));
    }
    OID__AllocObject_DefaultTag_00662b2c(uVar3 << 2);
    if (extraout_EAX == (undefined4 *)0x0) {
      return -0x7ff8fff2;
    }
    puVar4 = *(undefined4 **)((int)this + 0x58);
    puVar5 = extraout_EAX;
    for (uVar1 = *(uint *)((int)this + 0x5c) & 0x3fffffff; uVar1 != 0; uVar1 = uVar1 - 1) {
      *puVar5 = *puVar4;
      puVar4 = puVar4 + 1;
      puVar5 = puVar5 + 1;
    }
    for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
      *(undefined1 *)puVar5 = *(undefined1 *)puVar4;
      puVar4 = (undefined4 *)((int)puVar4 + 1);
      puVar5 = (undefined4 *)((int)puVar5 + 1);
    }
    OID__FreeObject_Callback(*(void **)((int)this + 0x58));
    *(undefined4 **)((int)this + 0x58) = extraout_EAX;
    *(uint *)((int)this + 0x60) = uVar3;
  }
  return 0;
}
